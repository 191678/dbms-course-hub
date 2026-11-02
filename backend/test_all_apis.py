"""Test all relevant API endpoints."""
import requests
import json

print("=== 1. Chapters API ===")
r = requests.get("http://localhost:8000/api/chapters/", timeout=3)
print(f"Status: {r.status_code}")
if r.ok:
    data = r.json()
    print(f"Count: {len(data)}")
    if data:
        ch = data[0]
        print(f"First chapter: {ch['title']}")
        print(f"  Knowledge points: {len(ch.get('knowledge_points', []))}")
        if ch.get('knowledge_points'):
            kp = ch['knowledge_points'][0]
            print(f"  First KP: {kp['content']}")
            print(f"    Questions: {len(kp.get('questions', []))}")
else:
    print(f"Error: {r.text[:200]}")

print()
print("=== 2. Questions API ===")
r2 = requests.get("http://localhost:8000/api/questions/", params={"limit": 5}, timeout=3)
print(f"Status: {r2.status_code}")
if r2.ok:
    data2 = r2.json()
    print(f"Count (limit 5): {len(data2)}")
    if data2:
        q = data2[0]
        print(f"First question: {q['stem'][:40]}")
        print(f"  Type: {q['type']}")
        print(f"  Options: {q['options']} (type: {type(q['options']).__name__})")
        print(f"  Answer: {q['answer']}")
else:
    print(f"Error: {r2.text[:200]}")

print()
print("=== 3. Knowledge Points API ===")
r3 = requests.get("http://localhost:8000/api/knowledge_points/", timeout=3)
print(f"Status: {r3.status_code}")
if r3.ok:
    data3 = r3.json()
    print(f"Count: {len(data3)}")
else:
    print(f"Error: {r3.text[:200]}")

print()
print("=== 4. Agent Visualize API ===")
r4 = requests.post("http://localhost:8000/api/agent/visualize/", json={"topic": "数据模型"}, timeout=10)
print(f"Status: {r4.status_code}")
if r4.ok:
    data4 = r4.json()
    print(f"Success: {data4.get('success')}")
    print(f"Knowledge point: {data4.get('knowledge_point')}")
    print(f"Chapter: {data4.get('chapter')}")
    if data4.get('diagram'):
        print(f"Diagram: format={data4['diagram'].get('format')}, content_len={len(data4['diagram'].get('content', ''))}")
else:
    print(f"Error: {r4.text[:200]}")

print()
print("=== 5. Knowledge Graph API ===")
r5 = requests.get("http://localhost:8000/api/knowledge_graph/relations/by-content/", params={"content": "数据模型"}, timeout=3)
print(f"Status: {r5.status_code}")
if r5.ok:
    data5 = r5.json()
    print(f"Success: {data5.get('success')}")
    print(f"Nodes: {len(data5.get('nodes', []))}")
    print(f"Edges: {len(data5.get('edges', []))}")
else:
    print(f"Error: {r5.text[:200]}")

print()
print("DONE")
