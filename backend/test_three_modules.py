"""Quick test of all three module APIs."""
import requests
import json

base = "http://localhost:8000"

# 1. Chapters API (for course homepage)
print("=== 1. Chapters API ===")
r = requests.get(f"{base}/api/chapters/", timeout=10)
data = r.json()
print(f"Status: {r.status_code}")
print(f"Chapters count: {len(data)}")
if data:
    first = data[0]
    print(f"First chapter: {first.get('title', 'N/A')}")
    kps = first.get('knowledge_points', [])
    print(f"Knowledge points in first chapter: {len(kps)}")

# 2. Questions API (for question bank)
print("\n=== 2. Questions API ===")
r = requests.get(f"{base}/api/questions/", timeout=10)
data = r.json()
print(f"Status: {r.status_code}")
if isinstance(data, list):
    print(f"Questions count: {len(data)}")
    if data:
        q = data[0]
        print(f"First question type: {q.get('type', 'N/A')}")
        print(f"First question options: {q.get('options', 'N/A')}")
        print(f"Options is list: {isinstance(q.get('options'), list)}")
elif isinstance(data, dict):
    print(f"Response keys: {list(data.keys())}")
    items = data.get('items', data.get('questions', []))
    print(f"Questions count: {len(items)}")

# 3. Visualize API (for knowledge visualization)
print("\n=== 3. Visualize API ===")
r = requests.post(f"{base}/api/agent/visualize/", json={"topic": "数据模型"}, timeout=10)
data = r.json()
print(f"Status: {r.status_code}")
print(f"Success: {data.get('success')}")
print(f"Has knowledge_point: {bool(data.get('knowledge_point'))}")
print(f"Has theory_content: {bool(data.get('theory_content'))}")
diagram = data.get('diagram')
if diagram:
    print(f"Diagram format: {diagram.get('format')}")
    print(f"Diagram content length: {len(diagram.get('content', ''))}")
else:
    print("No diagram returned!")

print("\n=== All API checks complete ===")
