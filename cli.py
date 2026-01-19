import os
import argparse
import json
from pathlib import Path
from typing import List

from pdf_parser import extract_text_by_section
from tree_generator import generate_concept_tree
from graph_manager import GraphManager
from models import PaperSchema

def process_pdf(pdf_path: Path, graph_manager: GraphManager):
    print(f"[*] Processing: {pdf_path.name}")
    
    try:
        # 1. Parse PDF
        sections = extract_text_by_section(str(pdf_path))
        
        # 2. Extract context for Gemini (Abstract + Intro + Conclusion)
        context_parts = []
        for s in ["Abstract", "Introduction", "Conclusion"]:
            if s in sections:
                context_parts.append(sections[s])
        
        if not context_parts:
            context_text = "\n\n".join(sections.values())[:8000]
        else:
            context_text = "\n\n".join(context_parts)

        # 3. Generate Concept Tree
        print(f"    - Generating concept tree with Gemini...")
        root_concept = generate_concept_tree(context_text)

        # 4. Integrate into Knowledge Graph
        paper = PaperSchema(title=pdf_path.stem, root_concept=root_concept)
        
        print(f"    - Embedding and linking concepts...")
        graph_manager.embed_and_store(paper)
        graph_manager.link_concepts(paper)
        
        print(f"    - Linked paper: {pdf_path.name}")
        return True
    except Exception as e:
        print(f"[!] Error processing {pdf_path.name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="ScholarGraph CLI: Convert PDFs to a knowledge graph JSON.")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to a PDF file or a directory containing PDFs")
    parser.add_argument("--output", "-o", type=str, default="graph_output.json", help="Path to save the final JSON graph (default: graph_output.json)")
    parser.add_argument("--threshold", "-t", type=float, default=0.85, help="Similarity threshold for cross-paper links (0.0 to 1.0, default: 0.85)")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"[!] Error: Input path '{args.input}' does not exist.")
        return

    # Initialize GraphManager
    graph_manager = GraphManager()
    
    pdfs_to_process: List[Path] = []
    if input_path.is_file():
        if input_path.suffix.lower() == ".pdf":
            pdfs_to_process.append(input_path)
        else:
            print(f"[!] Error: '{args.input}' is not a PDF file.")
            return
    elif input_path.is_dir():
        pdfs_to_process = list(input_path.glob("*.pdf"))
        if not pdfs_to_process:
            print(f"[!] Error: No PDF files found in directory '{args.input}'.")
            return
    
    print(f"[*] Found {len(pdfs_to_process)} PDF(s) to process.")
    
    success_count = 0
    for pdf in pdfs_to_process:
        if process_pdf(pdf, graph_manager):
            success_count += 1
            
    # Save the final graph
    print(f"[*] Saving final graph data to {output_path}...")
    graph_data = graph_manager.get_graph_json()
    with open(output_path, "w") as f:
        json.dump(graph_data, f, indent=2)
        
    print(f"[*] Done! Processed {success_count}/{len(pdfs_to_process)} papers.")
    print(f"[*] Final knowledge graph has {len(graph_data['nodes'])} nodes and {len(graph_data['links'])} edges.")
    
    # Analyze inter-paper links
    inter_links = [l for l in graph_data['links'] if l.get('type') == 'cross-paper']
    if inter_links:
        print(f"[*] Found {len(inter_links)} inter-paper relationships:")
        for l in inter_links:
            source_label = next((n['label'] for n in graph_data['nodes'] if n['id'] == l['source']), l['source'])
            target_label = next((n['label'] for n in graph_data['nodes'] if n['id'] == l['target']), l['target'])
            print(f"    - {source_label} <-> {target_label} (Sim: {l.get('weight', 'N/A'):.2f})")
    else:
        print("[!] No inter-paper relationships found at this threshold.")

if __name__ == "__main__":
    main()
