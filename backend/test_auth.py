import requests
import json

BASE = 'http://localhost:8000/api'

print('=== 测试学生登录系统 ===')

# 1. 测试注册
print('\n1. 测试注册...')
r = requests.post(f'{BASE}/auth/register', json={
    'student_id': '2024001',
    'username': 'admin',
    'password': 'admin123',
    'name': '管理员'
})
print(f'   状态: {r.status_code}')
print(f'   响应: {r.text[:200]}')

# 2. 测试登录
print('\n2. 测试登录...')
r2 = requests.post(f'{BASE}/auth/login', json={
    'account': '2024001',
    'password': 'admin123'
})
print(f'   状态: {r2.status_code}')
if r2.ok:
    data = r2.json()
    print(f'   Token: {data["access_token"][:50]}...')
    print(f'   用户: {json.dumps(data["user"], ensure_ascii=False)}')

# 3. 测试获取个人信息
print('\n3. 测试获取个人信息...')
token = r2.json()['access_token']
r3 = requests.get(f'{BASE}/auth/profile', headers={'Authorization': f'Bearer {token}'})
print(f'   状态: {r3.status_code}')
print(f'   响应: {r3.text[:200]}')

# 4. 测试学习进度
print('\n4. 测试学习进度API...')
r4 = requests.post(f'{BASE}/learning-progress/session/start', params={'student_id': '2024001'})
print(f'   会话启动: {r4.status_code}')
session_id = r4.json().get('session_id', '')

r5 = requests.post(f'{BASE}/learning-progress/records/', json={
    'session_id': session_id,
    'student_id': '2024001',
    'module_type': 'knowledge_visualization',
    'module_id': 'module-001',
    'module_name': '知识可视化',
    'knowledge_point_content': '数据模型',
    'duration_seconds': 120,
    'study_duration_minutes': 2,
    'status': 'viewing',
    'completion_percentage': 50.0,
    'interaction_count': 3,
    'last_study_time': '2024-01-15T10:30:00Z',
    'mastered_count': 5,
    'not_mastered_count': 2,
    'extra_data': {'test': True}
})
print(f'   创建学习记录: {r5.status_code}')
if r5.ok:
    rec = r5.json()
    print(f'   记录UUID: {rec.get("record_uuid")}')
    print(f'   模块名: {rec.get("module_name")}')
    print(f'   完成百分比: {rec.get("completion_percentage")}%')

# 5. 测试学习进度摘要
print('\n5. 测试学习进度摘要...')
r6 = requests.get(f'{BASE}/learning-progress/summary/', params={'student_id': '2024001'})
print(f'   状态: {r6.status_code}')
if r6.ok:
    summary = r6.json()
    print(f'   总时长: {summary.get("total_duration_seconds")}秒')
    print(f'   总学习分钟: {summary.get("total_study_minutes")}')
    print(f'   整体完成度: {summary.get("overall_completion_percentage")}%')

# 6. 测试学生进度
print('\n6. 测试学生进度查询...')
r7 = requests.get(f'{BASE}/auth/students/2024001/progress')
print(f'   状态: {r7.status_code}')
if r7.ok:
    progress = r7.json()
    print(f'   总学习时长: {progress.get("total_study_minutes")}分钟')
    print(f'   访问模块数: {progress.get("total_modules_accessed")}')
    print(f'   整体完成度: {progress.get("overall_completion_percentage")}%')

# 7. 测试错误密码
print('\n7. 测试错误密码...')
r8 = requests.post(f'{BASE}/auth/login', json={
    'account': '2024001',
    'password': 'wrongpassword'
})
print(f'   状态: {r8.status_code} - {r8.json().get("detail", "") if r8.ok else r8.text[:100]}')

print('\n=== 所有测试完成 ===')
