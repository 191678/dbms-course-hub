"""Test the visualize API response structure."""
import requests
import json

r = requests.post("http://localhost:8000/api/agent/visualize/", json={"topic": "数据模型"}, timeout=10)
data = r.json()
print(json.dumps(data, indent=2, ensure_ascii=False))
