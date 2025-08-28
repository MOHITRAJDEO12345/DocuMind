---
title: DocuMind
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
pinned: false
short_description: The DocuMind system, as outlined and implemented in this rep
license: mit
---

# DocuMind: Advanced Document Intelligence Platform

## Overview
DocuMind is an AI-powered document intelligence platform that transforms static PDF documents into interactive knowledge sources. It leverages Google's Gemini AI, ChromaDB, and Streamlit to provide semantic search, conversational question answering, and source attribution with confidence scores.

## Features
- Intelligent PDF ingestion and chunking
- Semantic search with Google Generative AI embeddings
- AI-powered question answering (Gemini 2.0)
- Source attribution: page numbers, file names, content previews
- Confidence scoring system (Very High to Very Low)
- Modern, responsive Streamlit web interface
- Dockerized for easy deployment (Hugging Face Spaces supported)

## Installation Guide

### 1. Clone the Repository
```bash
git clone https://huggingface.co/spaces/KingArthur111/DocuMind.git
cd DocuMind
```

### 2. Set Up Python Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run Locally
```bash
streamlit run src/streamlit_app.py
```

### 4. Docker Deployment
Build and run the app in Docker:
```bash
docker build -t documind .
docker run -p 8501:8501 documind
```

### 5. Hugging Face Spaces
Just push to your Hugging Face Space and it will auto-build using the provided Dockerfile.

## Usage
1. Upload one or more PDF documents.
2. Ask questions in natural language.
3. View answers with source citations, page numbers, and confidence scores.
4. Explore document context and preview relevant content.

## Screenshots
Add screenshots here to showcase:
- The document upload and QA interface
- Example answer with source attribution and confidence scores

```
![DocuMind Upload Screen](img\img1.png)
![DocuMind QA Screen](img\img2.png)
```

## Future Upgrades
- <Real-World Challenge: RAG systems struggle with context windows and multi-step reasoning>
- <Narrative Hook: " An AI that remembers conversations and connects the dots ">
- Build an advanced RAG system that maintains conversation memory, handles multi-turn queries, and retrieves from multiple data sources (documents, databases, APIs).
- Include advanced chunking, re-ranking, and query expansion techniques.
- Tech Stack: LangChain/LlamaIndex, vector databases, Redis, FastAPI, advanced embedding models
- Success Metrics: Handle 10+ turn conversations, improve accuracy to 90%

## References
See [WHITEPAPER.md](WHITEPAPER.md) for a full technical and business overview.

---
Built with ❤️ using Streamlit, Gemini AI, and ChromaDB
