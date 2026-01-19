import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="scholar_graph")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Get all items in s43856
res_s = collection.get(where={"paper_title": "s43856-022-00107-6"})
print(f"Nodes in Paper 1: {len(res_s['ids'])}")

# Get all items in rp1
res_r = collection.get(where={"paper_title": "rp1"})
print(f"Nodes in Paper 2: {len(res_r['ids'])}")

# For each node in rp1, find top 3 in s43856
for i, (id_r, doc_r) in enumerate(zip(res_r['ids'], res_r['documents'])):
    emb_r = embedder.encode(doc_r).tolist()
    results = collection.query(
        query_embeddings=[emb_r],
        n_results=3,
        where={"paper_title": "s43856-022-00107-6"}
    )
    print(f"\nNode: {id_r} ({doc_r[:50]}...)")
    for j in range(len(results['ids'][0])):
        sim = 1 - results['distances'][0][j]
        print(f"  -> Match: {results['ids'][0][j]} (Sim: {sim:.4f}) | {results['documents'][0][j][:50]}...")
    if i >= 5: break # only first few
