# ScholarGraph 

ScholarGraph is an AI-powered research assistant that transforms complex research papers into interactive, navigable knowledge graphs. It automatically extracts key concepts, links related ideas across different papers, and provides a beautiful full-screen visualization.

---

## Quick Setup Guide

This project is built with Python and FastAPI. Follow these steps to get it running on your local machine (Linux, macOS, or Windows).

### 1. Prerequisites

- **Python 3.10+** installed.
- **OpenAI API Key**: You'll need this to generate the concept trees.

### 2. Installation

Extract the zip file, open your terminal (or Command Prompt) in the project folder, and run:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a file named `.env` in the root directory (if it doesn't exist) and add your OpenAI API key:

```env
OPENAI_API_KEY=your_actual_api_key_here
```

### 4. Start the Application

Run the following command to start the server:

```bash
python main.py
```

Now, open your browser and go to:
**[http://localhost:8000](http://localhost:8000)**

---

## How to Use

1. **Sidebar Toggle**: Click the blue arrow tab on the left to show/hide the upload panel.
2. **Upload PDF**: Drag and drop a research paper (PDF) into the upload area or click to browse.
3. **Explore the Graph**:
   - **Click and Drag** to pan around.
   - **Mouse Wheel** to zoom in and out.
   - **Controls**: Use the buttons in the top-right to Reset, Zoom In, or Zoom Out.
4. **Automatic Linking**: As you upload more papers, the system will automatically find semantic connections between them!

---

## Project Structure

- `main.py`: The heart of the application (FastAPI server).
- `tree_generator.py`: AI logic using OpenAI (GPT-4o-mini) to extract concepts.
- `graph_manager.py`: Manages concept storage and semantic linking via ChromaDB.
- `pdf_parser.py`: Handles high-quality text extraction from PDFs.
- `static/`: The interactive web interface (Mermaid.js, Pan-Zoom, etc.).
- `chroma_db/`: Your local database where all extracted knowledge is saved.
- `requirements.txt`: List of all required Python packages.

---

## Tech Stack

- **LLM**: GPT-4o-mini (via LangChain)
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence-Transformers
- **Visualization**: Mermaid.js & svg-pan-zoom
- **Backend**: FastAPI
