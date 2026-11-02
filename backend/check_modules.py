import requests
import json

print("=== Chapters API ===")
r = requests.get("http://localhost:8000/api/chapters/", timeout=3)
print(f"Status: {r.status_code}")
data = r.json()
print(f"Count: {len(data)}")
if data:
    print(f"First: {json.dumps(data[0], ensure_ascii=False)[:300]}")

print()
print("=== Questions API ===")
r2 = requests.get("http://localhost:8000/api/questions/", timeout=3)
print(f"Status: {r2.status_code}")
d2 = r2.json()
if isinstance(d2, list):
    print(f"Count: {len(d2)}")
    if d2:
        print(f"First: {json.dumps(d2[0], ensure_ascii=False)[:300]}")
elif isinstance(d2, dict):
    print(f"Keys: {list(d2.keys())}")
    total = d2.get("total", "N/A")
    items_count = len(d2.get("items", d2.get("results", [])))
    print(f"Total: {total}, Items: {items_count}")

print()
print("=== Knowledge Points API ===")
r3 = requests.get("http://localhost:8000/api/knowledge_points/", timeout=3)
print(f"Status: {r3.status_code}")
d3 = r3.json()
if isinstance(d3, list):
    print(f"Count: {len(d3)}")
elif isinstance(d3, dict):
    print(f"Keys: {list(d3.keys())}")
    total = d3.get("total", "N/A")
    items = d3.get("items", d3.get("results", []))
    print(f"Total: {total}, Items: {len(items)}")

print()
print("=== Knowledge Graph Relations ===")
r4 = requests.get("http://localhost:8000/api/knowledge_graph/relations/", params={"content": "数据模型"}, timeout=3)
print(f"Status: {r4.status_code}")
if r4.ok:
    d4 = r4.json()
    print(f"Response: {json.dumps(d4, ensure_ascii=False)[:400]}")

print()
print("=== Auth Progress ===")
r5 = requests.get("http://localhost:8000/api/auth/students/2024001/progress", timeout=3)
print(f"Status: {r5.status_code}")
if r5.ok:
    d5 = r5.json()
    print(f"Data: {json.dumps(d5, ensure_ascii=False)[:400]}")

print()
print("DONE")
