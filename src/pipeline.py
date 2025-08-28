from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from typing import List

class RAGPipeline:
    def __init__(self, vector_store: Chroma, api_key: str):
        self.vector_store = vector_store
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            google_api_key=api_key,
            temperature=0.2,
        )
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Define the prompt template for the LLM
        # This template instructs the model to answer based on the provided context
        # and to include source citations.
        template = """
        You are a helpful assistant. Use the following context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        Context:
        {context}

        Question:
        {question}

        Instructions:
        1. Provide a detailed and accurate answer based ONLY on the provided context.
        2. When referencing information, mention which source and page it comes from.
        3. If the context doesn't contain enough information, say so clearly.
        4. Keep your answer concise but comprehensive.

        Answer:
        """
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

    def format_documents_with_citations(self, documents: List) -> str:
        """
        Formats the retrieved documents into a single string, including metadata for citations.
        """
        formatted_text = []
        for i, doc in enumerate(documents, 1):
            content = doc.page_content
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "unknown")
            formatted_text.append(f"Source {i}:\nFile: {source}\nPage: {page}\nContent:\n{content}\n")
        return "\n---\n".join(formatted_text)

    def get_source_info_with_scores(self, documents: List) -> str:
        """
        Gets source information with confidence scores for the retrieved documents.
        """
        source_info = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "unknown")

            # Calculate confidence score based on multiple factors:
            # 1. Retrieval order (higher for top results)
            # 2. Content length (longer content might be more relevant)
            # 3. Position in document (earlier pages might be more important)
            base_score = 1.0 - (i - 1) * 0.15  # Order factor
            length_factor = min(1.0, len(doc.page_content) / 1000)  # Length factor
            page_factor = max(0.8, 1.0 - (page - 1) * 0.05) if isinstance(page, int) else 1.0

            confidence_score = base_score * length_factor * page_factor
            confidence_score = max(0.1, min(1.0, confidence_score))  # Clamp between 0.1 and 1.0
            confidence_percent = int(confidence_score * 100)

            # Determine confidence level
            if confidence_percent >= 90:
                level = "Very High"
            elif confidence_percent >= 75:
                level = "High"
            elif confidence_percent >= 60:
                level = "Medium"
            elif confidence_percent >= 40:
                level = "Low"
            else:
                level = "Very Low"

            source_info.append(f"• **Source {i}**: {source}")
            source_info.append(f"  - **Page**: {page}")
            source_info.append(f"  - **Confidence**: {confidence_percent}% ({level})")
            source_info.append(f"  - **Content Preview**: {doc.page_content[:200]}...")

        return "\n".join(source_info)

    def answer_question(self, question: str) -> str:
        """
        Executes the RAG pipeline: retrieves documents and generates a response.
        """
        # Step 1: Retrieve relevant documents with scores
        retrieved_docs = self.retriever.get_relevant_documents(question)

        if not retrieved_docs:
            return "I am sorry, I could not find any relevant information in the documents to answer your question."

        # Step 2: Format the retrieved documents for the prompt
        formatted_context = self.format_documents_with_citations(retrieved_docs)

        # Step 3: Create the final prompt
        final_prompt = self.prompt.format(context=formatted_context, question=question)

        # Step 4: Call the LLM to generate the answer
        response = self.llm.invoke(final_prompt).content

        # Step 5: Add source information and confidence scores to the response
        source_info = self.get_source_info_with_scores(retrieved_docs)

        # Combine the response with source information
        full_response = f"{response}\n\n**Sources and Context:**\n{source_info}"

        return full_response