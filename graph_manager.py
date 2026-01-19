import chromadb
from chromadb.config import Settings
import networkx as nx
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from models import PaperSchema, ConceptNode

class GraphManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="scholar_graph",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.graph = nx.Graph()

    def _get_all_nodes_recursive(self, node: ConceptNode) -> List[ConceptNode]:
        nodes = [node]
        for child in node.children:
            nodes.extend(self._get_all_nodes_recursive(child))
        return nodes

    def embed_and_store(self, paper: PaperSchema):
        """Generates embeddings for all concepts in the paper and stores in ChromaDB."""
        all_nodes = self._get_all_nodes_recursive(paper.root_concept)
        
        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for node in all_nodes:
            # Create a unique ID for this paper-node combination
            unique_id = f"{paper.title}_{node.id}"
            
            # Create text for embedding: label + summary
            text_to_embed = f"{node.label}: {node.summary}"
            embedding = self.embedder.encode(text_to_embed).tolist()
            node.embedding = embedding # Update model with embedding

            # Prep for ChromaDB
            ids.append(unique_id)
            embeddings.append(embedding)
            metadatas.append({"label": node.label, "original_id": node.id, "paper_title": paper.title})
            documents.append(text_to_embed)

            # Add to NetworkX Graph
            self.graph.add_node(unique_id, label=node.label, summary=node.summary, type="concept", paper=paper.title)

        # Upsert into ChromaDB
        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )

    def link_concepts(self, paper: PaperSchema, threshold: float = 0.85) -> nx.Graph:
        """
        Links nodes in the new paper to existing nodes in the global graph
        based on cosine similarity (> threshold).
        """
        # First, add the internal edges of the tree structure to the graph
        self._add_tree_edges(paper.root_concept, paper.title)

        all_nodes = self._get_all_nodes_recursive(paper.root_concept)
        # print(f"      - Linking {len(all_nodes)} nodes for paper: {paper.title}")
        
        for node in all_nodes:
            if not node.embedding:
                # print(f"      [DEBUG] Missing embedding for node: {node.id}")
                continue
            
            unique_id = f"{paper.title}_{node.id}"
            
            # Query ChromaDB for similar nodes from OTHER papers
            results = self.collection.query(
                query_embeddings=[node.embedding],
                n_results=10,
                where={"paper_title": {"$ne": paper.title}}
            )

            # Link based on threshold
            for i in range(len(results['ids'][0])):
                neighbor_id = results['ids'][0][i]
                similarity = 1 - results['distances'][0][i] 

                if neighbor_id != unique_id:
                    # Check if it's between different papers
                    neighbor_paper = neighbor_id.split('_')[0]
                    current_paper = unique_id.split('_')[0]
                    
                    # print(f"      [DEBUG] Checking link to {neighbor_id} (Sim: {similarity:.4f})")
                    
                    if similarity > threshold:
                        edge_type = "cross-paper" if neighbor_paper != current_paper else "semantic-related"
                        self.graph.add_edge(unique_id, neighbor_id, weight=float(similarity), type=edge_type)
                        if neighbor_paper != current_paper:
                            print(f"      [LINK] !!! FOUND CROSS-PAPER LINK: {node.id} -> {neighbor_id} (Sim: {similarity:.2f})")
        
        return self.graph

    def _add_tree_edges(self, node: ConceptNode, paper_title: str):
        """Recursively add hierarchical edges within the paper's tree."""
        for child in node.children:
            u_id = f"{paper_title}_{node.id}"
            v_id = f"{paper_title}_{child.id}"
            self.graph.add_edge(u_id, v_id, type="hierarchical")
            self._add_tree_edges(child, paper_title)

    def get_graph_json(self) -> Dict[str, Any]:
        """Returns the current NetworkX graph as a JSON-serializable dictionary."""
        return nx.node_link_data(self.graph, edges="links")

if __name__ == "__main__":
    # Quick test
    gm = GraphManager()
    print("Graph Manager Initialized.")
