import os
import shutil
from pathlib import Path
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from pdf_parser import extract_text_by_section
from tree_generator import generate_concept_tree
from graph_manager import GraphManager
from models import PaperSchema, ConceptNode

app = FastAPI(title="ScholarGraph API")

# Setup directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global Graph Manager
gm = GraphManager()

class ProcessResponse(BaseModel):
    status: str
    message: str
    paper_title: str

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.post("/upload", response_model=ProcessResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 1. Parse PDF
        sections = extract_text_by_section(str(file_path))
        
        # 2. Extract context
        context_parts = []
        for s in ["Abstract", "Introduction", "Conclusion"]:
            if s in sections:
                context_parts.append(sections[s])
        
        context_text = "\n\n".join(context_parts) if context_parts else "\n\n".join(sections.values())[:8000]
        
        # 3. Generate Concept Tree
        root_concept = generate_concept_tree(context_text)
        
        # 4. Integrate into Knowledge Graph
        paper_title = file_path.stem
        paper = PaperSchema(title=paper_title, root_concept=root_concept)
        
        gm.embed_and_store(paper)
        gm.link_concepts(paper)
        
        return ProcessResponse(
            status="success", 
            message=f"Processed {file.filename} successfully", 
            paper_title=paper_title
        )
    except Exception as e:
        print(f"Error processing {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph")
async def get_graph():
    """Returns the global graph data in JSON format."""
    return gm.get_graph_json()

@app.get("/graph/mermaid")
async def get_mermaid():
    """Returns the graph data formatted for Mermaid.js."""
    graph_data = gm.get_graph_json()
    nodes = graph_data.get('nodes', [])
    links = graph_data.get('links', [])
    
    def wrap_label(label: str, max_chars: int = 20) -> str:
        words = label.split()
        lines = []
        current_line = []
        current_length = 0
        for word in words:
            if current_length + len(word) > max_chars:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1
        if current_line:
            lines.append(" ".join(current_line))
        return "<br/>".join(lines)

    mermaid_lines = ["graph TD"]
    
    # Track node labels for Mermaid
    node_map = {n['id']: wrap_label(n['label'].replace('"', "'")) for n in nodes}
    
    for link in links:
        src = link['source']
        tgt = link['target']
        ltype = link.get('type', 'hierarchical')
        
        src_label = node_map.get(src, src)
        tgt_label = node_map.get(tgt, tgt)
        
        if ltype == 'hierarchical':
            mermaid_lines.append(f'    {src}["{src_label}"] --> {tgt}["{tgt_label}"]')
        else:
            weight = link.get('weight', 0.85)
            # Use dotted lines for cross-paper semantic links
            mermaid_lines.append(f'    {src}["{src_label}"] -. "Sim: {weight:.2f}" .-> {tgt}["{tgt_label}"]')
            
    return {"mermaid": "\n".join(mermaid_lines)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
