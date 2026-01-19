import json
import os
from pdf_parser import extract_text_by_section
from tree_generator import generate_concept_tree
from graph_manager import GraphManager
from models import PaperSchema

def test_full_pipeline():
    print("Initializing Graph Manager...")
    gm = GraphManager()
    
    # List of papers to process (provided in the project root)
    test_papers = ["rp1.pdf", "s43856-022-00107-6.pdf"]
    
    for paper_file in test_papers:
        if not os.path.exists(paper_file):
            print(f"Warning: {paper_file} not found. Skipping.")
            continue
            
        print(f"\n>>> Processing {paper_file}...")
        
        try:
            # 1. Extract sections
            sections = extract_text_by_section(paper_file)
            print(f"Extracted {len(sections)} sections.")
            
            # Combine major sections for LLM context
            context_parts = []
            for s in ["Abstract", "Introduction", "Conclusion"]:
                if s in sections:
                    context_parts.append(sections[s])
            
            context_text = "\n\n".join(context_parts) if context_parts else "\n\n".join(sections.values())[:8000]
            
            # 2. Generate Tree
            print("Generating concept tree with Gemini...")
            root_concept = generate_concept_tree(context_text)
            print(f"Tree generated with {len(root_concept.children)} main branches.")
            
            # 3. Link and Store
            paper = PaperSchema(title=paper_file.replace(".pdf", ""), root_concept=root_concept)
            
            print("Embedding and storing concepts...")
            gm.embed_and_store(paper)
            
            print("Linking concepts based on similarity...")
            gm.link_concepts(paper)
            
        except Exception as e:
            print(f"Error processing {paper_file}: {e}")

    # Final Graph Stats
    print("\n--- Final Knowledge Graph Summary ---")
    print(f"Total Nodes: {len(gm.graph.nodes)}")
    print(f"Total Edges: {len(gm.graph.edges)}")
    
    # Save output for inspection
    with open("test_graph_output.json", "w") as f:
        json.dump(gm.get_graph_json(), f, indent=2)
    print("Graph saved to test_graph_output.json")

if __name__ == "__main__":
    test_full_pipeline()
