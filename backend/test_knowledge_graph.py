"""Test knowledge graph API."""
import requests

base = "http://localhost:8000"

# Test by-content endpoint
print("=== Knowledge Graph by-content ===")
r = requests.get(f"{base}/api/knowledge_graph/relations/by-content/", params={"content": "数据模型"}, timeout=10)
data = r.json()
print(f"Status: {r.status_code}")
print(f"Success: {data.get('success')}")
print(f"Nodes: {len(data.get('nodes', []))}")
print(f"Edges: {len(data.get('edges', []))}")
if data.get('current_knowledge_point'):
    print(f"Current KP: {data['current_knowledge_point'].get('label')}")

# Test relation-types endpoint
print("\n=== Relation Types ===")
r = requests.get(f"{base}/api/knowledge_graph/relation-types/", timeout=10)
data = r.json()
print(f"Status: {r.status_code}")
print(f"Relation types: {list(data.keys())}")
