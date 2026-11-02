import pymysql
import json

conn = pymysql.connect(host='localhost', user='root', password='mysql', database='dbms_course_hub')
cursor = conn.cursor()

more_questions = [
    (6, '判断', '用户定义完整性可以通过CHECK约束实现。', None, '正确', 'CHECK约束可以实现用户定义的完整性规则。'),
    (7, '判断', 'DISTINCT关键字用于去除重复行。', None, '正确', 'DISTINCT关键字用于去除查询结果中的重复行。'),
    (8, '判断', 'LIKE运算符不区分大小写。', None, '错误', 'LIKE运算符是否区分大小写取决于数据库的配置。'),
    (9, '判断', 'COUNT(*)会统计包括NULL在内的所有行。', None, '正确', 'COUNT(*)统计所有行，包括含有NULL值的行。'),
    (10, '判断', 'CROSS JOIN是笛卡尔积连接。', None, '正确', 'CROSS JOIN返回两个表的笛卡尔积。'),
    (11, '判断', '弱实体需要依赖于强实体才能存在。', None, '正确', '弱实体没有主键，需要依赖强实体。'),
    (12, '判断', 'BCNF是比3NF更高的范式。', None, '正确', 'BCNF（Boyce-Codd范式）是3NF的改进。'),
    (13, '判断', '视图可以提供数据安全性。', None, '正确', '通过视图可以限制用户访问的数据范围。'),
    (14, '判断', '哈希函数是不可逆的。', None, '正确', '哈希函数是单向函数，无法从哈希值还原原始数据。'),
]

insert_sql = """
INSERT INTO questions (knowledge_point_id, type, stem, options, answer, analysis, created_at, updated_at)
VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
"""

cursor.executemany(insert_sql, more_questions)
conn.commit()

print(f'成功插入 {cursor.rowcount} 条题目')

cursor.execute('SELECT kp.id, kp.content, COUNT(q.id) as q_count FROM knowledge_points kp LEFT JOIN questions q ON kp.id = q.knowledge_point_id GROUP BY kp.id, kp.content ORDER BY kp.id')
print('\n最终知识点题目数量统计:')
for row in cursor.fetchall():
    print(f'知识点{row[0]}: {row[1]} - {row[2]}道题')

conn.close()
