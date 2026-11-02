import pymysql
import json

conn = pymysql.connect(host='localhost', user='root', password='mysql', database='dbms_course_hub', charset='utf8mb4')
cursor = conn.cursor()

data = {
    'category': '基础概念',
    'detail_content': '数据库系统是由数据库、数据库管理系统（DBMS）、应用程序和数据库管理员组成的完整系统。',
    'key_points': json.dumps(['数据库系统组成', '数据库定义', 'DBMS功能']),
    'image_prompt': 'Database system architecture diagram',
    'video_script': '步骤1: 介绍数据库系统\n步骤2: 演示DBMS功能\n步骤3: 总结优势'
}

update_sql = """
UPDATE knowledge_points 
SET category = %s, detail_content = %s, key_points = %s, image_prompt = %s, video_script = %s, updated_at = NOW()
WHERE id = %s
"""

total_updated = 0
for kp_id in range(1, 31):
    try:
        cursor.execute(update_sql, (data['category'], data['detail_content'], data['key_points'], data['image_prompt'], data['video_script'], kp_id))
        total_updated += cursor.rowcount
    except:
        pass

print(f"Updated {total_updated} knowledge points")
conn.commit()
conn.close()
