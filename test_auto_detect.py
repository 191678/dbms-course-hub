import requests

r = requests.post('http://localhost:8000/api/agent/chat', json={'student_question': '画一下B+树'})
result = r.json()
print(f'Tool used: {result["tool_used"]}')
print(f'Has image: {"Yes" if result["image_url"] else "No"}')
print(f'Answer: {result["answer"][:100]}')

r2 = requests.post('http://localhost:8000/api/agent/chat', json={'student_question': '演示ACID事务'})
result2 = r2.json()
print(f'\nTool used: {result2["tool_used"]}')
print(f'Answer: {result2["answer"][:100]}')
