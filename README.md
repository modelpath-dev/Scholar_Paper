# ScholarGraph: AI-Powered Research Knowledge Explorer

ScholarGraph is an intelligent system designed to help researchers navigate and connect scientific concepts across large volumes of research papers. By combining PDF parsing, LLM-based concept extraction, and vector-based semantic linking, ScholarGraph builds a dynamic, evolving knowledge graph of scientific insights.

## Key Features

- **Automated Concept Extraction**: Uses Gemini Pro to identify core methods, findings, and sub-concepts from research papers.
- **Semantic Linking**: Automatically discovers and links related concepts across different papers using vector embeddings.
- **Hierarchical Representation**: Organizes paper content into an intuitive, multi-level concept tree.
- **Persistent Knowledge Graph**: Maintains a global search and storage system using ChromaDB.
- **FastAPI Integration**: Robust backend API for paper processing and graph retrieval.

## Quick Start

- [Installation & Usage](./USAGE.md)
- [System Architecture](./ARCHITECTURE.md)

## How to Use (CLI)

```bash
python cli.py --input path/to/papers --output graph.json
```

## Technologies Used

- **Backend**: FastAPI, Python 3.8+
- **LLM**: Google Gemini Pro (via LangChain)
- **Vector DB**: ChromaDB
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Graph Logic**: NetworkX
- **PDF Parsing**: PyMuPDF
- **Frontend**: Vanilla JS, Cytoscape.js (Visualization upcoming)

## Project Structure

- `main.py`: Entry point for the FastAPI application.
- `pdf_parser.py`: PDF text and section extraction.
- `tree_generator.py`: LLM-based concept tree generation.
- `graph_manager.py`: Global knowledge graph and vector storage management.
- `models.py`: Pydantic data models.
- `static/`: Frontend web interface files.
- `chroma_db/`: Local persistent vector storage.
