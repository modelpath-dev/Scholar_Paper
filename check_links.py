import json

with open("final_knowledge_graph.json", "r") as f:
    data = json.load(f)

print(f"Total Nodes: {len(data['nodes'])}")
print(f"Total Links: {len(data['links'])}")

inter_paper_links = []
for link in data['links']:
    source_paper = link['source'].split('_')[0]
    target_paper = link['target'].split('_')[0]
    if source_paper != target_paper:
        inter_paper_links.append(link)

print(f"Inter-paper links found: {len(inter_paper_links)}")
for link in inter_paper_links:
    print(f"Link: {link['source']} <-> {link['target']} (Weight: {link.get('weight', 'N/A')})")
