import requests
import time

print("=== 测试学习进度API ===")

time.sleep(2)

# 测试模块类型
try:
    r = requests.get('http://localhost:8000/api/learning-progress/module-types/', timeout=5)
    print(f"模块类型: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"模块类型列表: {list(data.get('module_types', {}).keys())}")
except Exception as e:
    print(f"模块类型测试失败: {e}")

# 测试创建会话
try:
    r = requests.post('http://localhost:8000/api/learning-progress/session/start?student_id=test_student', timeout=5)
    print(f"\n创建会话: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        session_id = data.get('session_id')
        print(f"会话ID: {session_id}")
        
        # 测试创建学习记录
        record_data = {
            "session_id": session_id,
            "student_id": "test_student",
            "module_type": "knowledge_visualization",
            "module_id": "test_module",
            "knowledge_point_content": "数据模型",
            "duration_seconds": 30,
            "status": "viewing",
            "interaction_count": 1,
            "metadata": {"test": True}
        }
        r2 = requests.post('http://localhost:8000/api/learning-progress/records/', json=record_data, timeout=5)
        print(f"\n创建学习记录: {r2.status_code}")
        if r2.status_code == 200:
            print(f"记录ID: {r2.json().get('id')}")
        
        # 测试获取学习记录
        r3 = requests.get(f'http://localhost:8000/api/learning-progress/records/?session_id={session_id}', timeout=5)
        print(f"\n获取学习记录: {r3.status_code}")
        if r3.status_code == 200:
            records = r3.json()
            print(f"记录数量: {len(records)}")
        
        # 测试获取学习进度摘要
        r4 = requests.get('http://localhost:8000/api/learning-progress/summary/?student_id=test_student', timeout=5)
        print(f"\n获取学习进度摘要: {r4.status_code}")
        if r4.status_code == 200:
            summary = r4.json()
            print(f"总学习时长: {summary.get('total_duration_seconds')}秒")
            print(f"总记录数: {summary.get('total_records')}")
            print(f"访问模块: {summary.get('modules_visited')}")
            print(f"知识点: {len(summary.get('knowledge_points_learned', []))}个")
        
        # 测试结束会话
        r5 = requests.post(f'http://localhost:8000/api/learning-progress/session/end/{session_id}', timeout=5)
        print(f"\n结束会话: {r5.status_code}")
        if r5.status_code == 200:
            print(f"会话统计: {r5.json()}")
except Exception as e:
    print(f"学习进度测试失败: {e}")

print("\n=== 学习进度API测试完成 ===")