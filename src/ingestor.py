import os
import streamlit as st
import fitz  # PyMuPDF
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import hashlib
import json

class Ingestor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Ensure an event loop is available for GoogleGenerativeAIEmbeddings
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())

        # Initialize the embedding model
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=self.api_key,
        )

    def load_and_chunk_pdfs(self, file_paths: List[str]) -> List:
        """Loads PDFs and splits them into chunks with metadata."""
        all_chunks = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""],
            length_function=len
        )

        for file_path in file_paths:
            try:
                # Use PyMuPDF to open and extract text from the PDF
                doc = fitz.open(file_path)
                
                # Extract text page by page with metadata
                for page_num, page in enumerate(doc):
                    text = page.get_text()
                    
                    # Create LangChain Document object with metadata
                    langchain_doc = Document(
                        page_content=text,
                        metadata={
                            "source": os.path.basename(file_path),
                            "page": page_num + 1,
                        }
                    )
                    
                    # Split the page text into chunks
                    chunks = text_splitter.split_documents([langchain_doc])
                    all_chunks.extend(chunks)
                
                doc.close()
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                
        return all_chunks

    def ingest_documents(self, file_paths: List[str]):
        """Ingests documents, creates embeddings, and initializes a ChromaDB vector store."""
        
        # Check if vector store cache exists, and load if it does
        # The cache key is a hash of the file paths, ensuring it's unique per set of docs
        cache_key = hashlib.sha256(json.dumps(sorted(file_paths)).encode()).hexdigest()
        
        # Using a fixed directory for persistence
        persist_directory = "./data/db"
        
        # Check if the vector store has been created and cached before
        if os.path.exists(persist_directory):
            print("Loading existing vector store from cache...")
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings,
            )
            # A simple check to ensure the vector store is not empty
            if vector_store.get()['documents']:
                return vector_store
        
        print("Creating new vector store from documents...")
        # Load and chunk documents
        chunks = self.load_and_chunk_pdfs(file_paths)
        if not chunks:
            raise ValueError("No valid document chunks could be created.")
            
        # Create the ChromaDB vector store from the chunks and embeddings
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=persist_directory,
        )
        # Persist the vector store to disk
        vector_store.persist()
        return vector_store