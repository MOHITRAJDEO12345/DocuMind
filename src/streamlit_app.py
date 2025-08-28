import asyncio
import altair as alt
import numpy as np
import pandas as pd

import streamlit as st

from dotenv import load_dotenv
import os
from ingestor import Ingestor
from pipeline import RAGPipeline
import tempfile

# Set the event loop policy for Windows (if available)
try:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except AttributeError:
    # WindowsSelectorEventLoopPolicy not available, use default
    pass

# 1. Set up the Streamlit page configuration and title
st.set_page_config(page_title="📄 DocuMind: Your Document AI", page_icon="📄")
st.title("📄 DocuMind: Document QA with Gemini")

# 2. Add a sidebar for API key and instructions
with st.sidebar:
    st.header("Configuration")
    st.info("To get started, please upload your PDF document(s).")
    gemini_api_key = st.text_input("Gemini API Key", type="password")

    # Check for API key and load from.env if available
    if not gemini_api_key:
        load_dotenv()
        gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        st.warning("Please enter a valid Gemini API key!")
        st.stop()

# Store API key in session state for reuse
st.session_state["gemini_api_key"] = gemini_api_key

# 3. Handle file uploads
uploaded_files = st.file_uploader(
    "Upload your PDF documents",
    type="pdf",
    accept_multiple_files=True,
)

# Use st.session_state to handle RAG state persistence across reruns
if "rag_pipeline" not in st.session_state:
    st.session_state["rag_pipeline"] = None
    st.session_state["ingested_docs"] = []

# 4. Ingest documents and set up the RAG pipeline
if uploaded_files and st.session_state["rag_pipeline"] is None:
    with st.spinner("Processing documents... This may take a moment."):
        # Create a temporary directory to save uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            file_paths = []
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(file_path)

            try:
                # Ingest documents and create the ChromaDB vector store
                ingestor = Ingestor(api_key=gemini_api_key)
                vector_store = ingestor.ingest_documents(file_paths)
                
                # Initialize the RAG pipeline with the vector store
                st.session_state["rag_pipeline"] = RAGPipeline(
                    vector_store=vector_store,
                    api_key=gemini_api_key,
                )
                
                # Store the names of the ingested documents for display
                st.session_state["ingested_docs"] = [f.name for f in uploaded_files]
                
                st.success("Documents processed successfully!")
                
            except Exception as e:
                st.error(f"An error occurred during document ingestion: {e}")
                st.session_state["rag_pipeline"] = None

# 5. Display a list of ingested documents
if st.session_state["ingested_docs"]:
    with st.expander("Documents in Knowledge Base"):
        st.write("The following documents have been successfully ingested:")
        for doc_name in st.session_state["ingested_docs"]:
            st.markdown(f"- {doc_name}")

# 6. Set up the chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process user question if RAG pipeline is ready
if st.session_state["rag_pipeline"]:
    question = st.chat_input("Ask a question about the documents...")
    
    if question:
        # Display user message
        st.session_message = st.chat_message("user")
        st.session_message.markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Get the answer from the RAG pipeline
                    response = st.session_state["rag_pipeline"].answer_question(question)
                    
                    # Display the response using st.markdown
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    st.error(f"An error occurred during response generation: {e}")