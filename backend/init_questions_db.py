"""
为每个知识点精确配置10道题目，ID从1开始连续编号。
题型分布：3道单选、2道多选、2道判断、2道填空、1道SQL编程
"""
import pymysql
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(host='localhost', user='root', password='mysql', database='dbms_course_hub', charset='utf8mb4')
cursor = conn.cursor()

# 获取所有知识点
cursor.execute('SELECT id, content, category, detail_content FROM knowledge_points ORDER BY id')
knowledge_points = cursor.fetchall()
print(f'共 {len(knowledge_points)} 个知识点')

# 清空现有题目
cursor.execute('DELETE FROM questions')
conn.commit()
# 重置自增ID从1开始
cursor.execute('ALTER TABLE questions AUTO_INCREMENT = 1')
conn.commit()
print('已清空题目表并重置自增ID')


def generate_questions_for_kp(kp_id, kp_content, kp_category, kp_detail):
    """为每个知识点生成10道题目"""
    title = kp_content
    questions = []

    # Q1: 单选 - 基本概念
    q1_stem = f'关于"{title}"，下列说法正确的是？'
    q1_options = [f'{title}是数据库系统中的重要概念', f'{title}与数据库无关', f'{title}仅存在于理论中', f'{title}已经过时']
    q1 = (kp_id, '单选', 'easy', q1_stem, json.dumps(q1_options, ensure_ascii=False), 'A',
          f'{title}是数据库系统中的基本概念，需要深入理解。')

    # Q2: 单选 - 细节理解
    q2_stem = f'下列关于"{title}"的描述，哪一项是正确的？'
    q2_options = [f'{title}属于数据库核心知识', f'{title}不需要学习', f'{title}仅适用于小型数据库', f'{title}与数据无关']
    q2 = (kp_id, '单选', 'medium', q2_stem, json.dumps(q2_options, ensure_ascii=False), 'A',
          f'{title}是数据库系统的核心知识之一。')

    # Q3: 单选 - 应用场景
    q3_stem = f'在实际应用中，"{title}"的主要作用是什么？'
    q3_options = [f'提高数据库的可靠性和效率', f'增加数据库的存储空间', f'简化数据库的设计', f'以上都不是']
    q3 = (kp_id, '单选', 'medium', q3_stem, json.dumps(q3_options, ensure_ascii=False), 'A',
          f'{title}在实际应用中主要用于提高数据库的可靠性和效率。')

    # Q4: 多选 - 特征/组成
    q4_stem = f'关于"{title}"，以下哪些描述是正确的？'
    q4_options = [f'{title}是数据库系统的基础', f'{title}涉及数据管理', f'{title}与数据库设计相关', f'{title}影响系统性能']
    q4 = (kp_id, '多选', 'medium', q4_stem, json.dumps(q4_options, ensure_ascii=False), 'ABCD',
          f'{title}涉及数据库系统的多个方面。')

    # Q5: 多选 - 应用
    q5_stem = f'"{title}"在实际应用中可以解决哪些问题？'
    q5_options = [f'数据管理问题', f'数据安全问题', f'数据一致性问题', f'数据存储问题']
    q5 = (kp_id, '多选', 'hard', q5_stem, json.dumps(q5_options, ensure_ascii=False), 'ABCD',
          f'{title}在数据库应用中可以解决多方面问题。')

    # Q6: 判断 - 正确
    q6_stem = f'"{title}"是数据库系统中的基本概念，对数据库设计和实现具有重要意义。'
    q6 = (kp_id, '判断', 'easy', q6_stem, None, '正确',
          f'{title}确实是数据库系统中的基本概念。')

    # Q7: 判断 - 错误
    q7_stem = f'"{title}"在数据库系统中可有可无，不影响系统的正常运行。'
    q7 = (kp_id, '判断', 'medium', q7_stem, None, '错误',
          f'{title}对数据库系统正常运行至关重要。')

    # Q8: 填空 - 概念填空
    q8_stem = f'请简述"{title}"的定义及其在数据库系统中的作用。'
    q8 = (kp_id, '填空', 'medium', q8_stem, None, f'{title}是数据库系统的重要概念',
          f'{title}是数据库系统中的重要概念，需要理解其定义和作用。')

    # Q9: 填空 - 应用填空
    q9_stem = f'请描述"{title}"在实际数据库应用中的具体使用场景和注意事项。'
    q9 = (kp_id, '填空', 'hard', q9_stem, None, f'{title}应用于数据库管理',
          f'{title}在实际应用中需要根据具体场景灵活运用。')

    # Q10: SQL编程
    q10_stem = f'请编写SQL语句，演示与"{title}"相关的数据库操作（如创建表、查询数据或设置约束等）。'
    q10 = (kp_id, 'SQL编程', 'hard', q10_stem, None, 'CREATE TABLE example (id INT PRIMARY KEY, name VARCHAR(100));',
           f'编写与{title}相关的SQL语句，考察对知识点的实际应用能力。')

    questions = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]
    return questions


# 为每个知识点生成10道题目
all_questions = []
for kp in knowledge_points:
    kp_id, kp_content, kp_category, kp_detail = kp
    qs = generate_questions_for_kp(kp_id, kp_content, kp_category, kp_detail)
    all_questions.extend(qs)

print(f'共生成 {len(all_questions)} 道题目')

# 批量插入
insert_sql = """
INSERT INTO questions (knowledge_point_id, type, difficulty, stem, options, answer, analysis, order_index, created_at, updated_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
"""

# 为每道题设置 order_index
final_questions = []
for idx, q in enumerate(all_questions):
    kp_id, q_type, difficulty, stem, options, answer, analysis = q
    order_index = (idx % 10) + 1  # 每个知识点的题目 order_index 从1到10
    final_questions.append((kp_id, q_type, difficulty, stem, options, answer, analysis, order_index))

cursor.executemany(insert_sql, final_questions)
conn.commit()
print(f'成功插入 {cursor.rowcount} 条题目')

# 验证结果
cursor.execute('SELECT MIN(id), MAX(id), COUNT(*) FROM questions')
r = cursor.fetchone()
print(f'\n题目ID范围: {r[0]} - {r[1]}, 总数: {r[2]}')

# 验证ID连续性
cursor.execute('SELECT id FROM questions ORDER BY id')
ids = [row[0] for row in cursor.fetchall()]
expected = list(range(1, len(ids) + 1))
if ids == expected:
    print('ID验证: 从1开始连续编号 ✓')
else:
    print(f'ID验证: 失败! 期望 1-{len(ids)}, 实际 {ids[0]}-{ids[-1]}')
    # 找出缺失的ID
    missing = set(expected) - set(ids)
    if missing:
        print(f'  缺失的ID: {sorted(missing)}')
    # 找出重复的ID
    duplicates = [i for i in ids if ids.count(i) > 1]
    if duplicates:
        print(f'  重复的ID: {set(duplicates)}')

# 验证每个知识点10道题
cursor.execute('''
    SELECT kp.id, kp.content, COUNT(q.id) as q_count
    FROM knowledge_points kp
    LEFT JOIN questions q ON kp.id = q.knowledge_point_id
    GROUP BY kp.id, kp.content
    HAVING q_count != 10
    ORDER BY kp.id
''')
wrong_kps = cursor.fetchall()
if not wrong_kps:
    print('每个知识点题目数量验证: 全部为10道 ✓')
else:
    print(f'以下知识点题目数量不为10:')
    for row in wrong_kps:
        print(f'  知识点{row[0]}: {row[1]} - {row[2]}道题')

# 验证题型分布
cursor.execute('SELECT type, COUNT(*) FROM questions GROUP BY type ORDER BY type')
print('\n题型分布:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}道')

# 验证填空题存在
cursor.execute("SELECT COUNT(*) FROM questions WHERE type = '填空'")
fill_count = cursor.fetchone()[0]
print(f'\n填空题数量: {fill_count}')

conn.close()
print('\n数据库初始化完成!')
