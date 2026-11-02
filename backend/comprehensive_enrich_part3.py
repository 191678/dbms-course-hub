# -*- coding: utf-8 -*-
"""
全面扩充知识点内容 - 第3章 SQL语言 (KP11-17)
"""
from app.database import SessionLocal
from app.models import KnowledgePoint

db = SessionLocal()

ENRICHMENTS = {}

# ===================== 第三章 SQL语言 (KP11-17) =====================

ENRICHMENTS[11] = {
    "detail_content": (
        "SQL（Structured Query Language，结构化查询语言）是关系数据库的标准语言，"
        "它集数据定义、数据操纵、数据控制于一体，是目前使用最广泛的数据库语言。\n\n"
        "SQL的数据定义语言（DDL，Data Definition Language）用于定义数据库的结构，"
        "包括模式、表、视图、索引等数据库对象的创建、修改和删除。\n\n"
        "【模式定义】\n"
        "SQL标准中，模式（Schema）是数据库对象的命名空间，一个模式可以包含表、视图、索引等对象。\n"
        "创建模式：CREATE SCHEMA <模式名> AUTHORIZATION <用户名>;\n"
        "删除模式：DROP SCHEMA <模式名> [CASCADE | RESTRICT];\n"
        "其中CASCADE表示级联删除（删除模式及其所有对象），RESTRICT表示限制删除（模式中有对象则不允许删除）。\n\n"
        "【基本表的定义】\n"
        "创建基本表：\n"
        "CREATE TABLE <表名> (\n"
        "    <列名> <数据类型> [列级完整性约束],\n"
        "    ...\n"
        "    [表级完整性约束]\n"
        ");\n"
        "常见数据类型：INT/INTEGER（整数）、FLOAT/REAL（浮点数）、CHAR(n)（定长字符串）、VARCHAR(n)（变长字符串）、DATE（日期）、TIME（时间）、BOOLEAN（布尔值）等。\n"
        "常见约束：PRIMARY KEY（主码）、FOREIGN KEY（外码）、NOT NULL（非空）、UNIQUE（唯一）、CHECK（检查条件）、DEFAULT（默认值）。\n\n"
        "【基本表的修改】\n"
        "1. 增加列：ALTER TABLE <表名> ADD <新列名> <数据类型> [约束];\n"
        "2. 删除列：ALTER TABLE <表名> DROP COLUMN <列名> [CASCADE | RESTRICT];\n"
        "3. 修改列：ALTER TABLE <表名> ALTER COLUMN <列名> <数据类型>;\n"
        "4. 增加约束：ALTER TABLE <表名> ADD CONSTRAINT <约束名> <约束定义>;\n"
        "5. 删除约束：ALTER TABLE <表名> DROP CONSTRAINT <约束名>;\n\n"
        "【基本表的删除】\n"
        "DROP TABLE <表名> [CASCADE | RESTRICT];\n"
        "CASCADE：级联删除，表及其依赖对象（如视图、约束）都被删除。\n"
        "RESTRICT：限制删除，如果有依赖对象则拒绝删除。\n\n"
        "【索引的定义与删除】\n"
        "索引是提高查询效率的重要机制。\n"
        "创建索引：CREATE [UNIQUE] [CLUSTER] INDEX <索引名> ON <表名>(<列名> [ASC|DESC], ...);\n"
        "UNIQUE表示索引列值唯一；CLUSTER表示聚簇索引（改变数据物理存储顺序）。\n"
        "删除索引：DROP INDEX <索引名>;\n\n"
        "【视图的定义】\n"
        "创建视图：CREATE VIEW <视图名> [(<列名>,...)] AS <子查询> [WITH CHECK OPTION];\n"
        "WITH CHECK OPTION表示对视图进行更新操作时，要保证更新的行满足视图定义的条件。\n"
        "删除视图：DROP VIEW <视图名> [CASCADE];"
    ),
    "key_points": [
        "DDL三大操作：CREATE（创建）、ALTER（修改）、DROP（删除）",
        "CREATE TABLE定义表结构，需指定列名、数据类型和完整性约束",
        "ALTER TABLE可增删改列、增删约束",
        "DROP TABLE删除表，CASCADE级联删除依赖对象",
        "索引提高查询效率，CREATE INDEX创建，分UNIQUE和CLUSTER"
    ],
    "learning_steps": [
        "第一步：理解DDL的作用——定义数据库结构（模式、表、索引、视图）",
        "第二步：掌握CREATE TABLE语法，熟悉常见数据类型和约束",
        "第三步：掌握ALTER TABLE的五种修改操作（加列、删列、改列、加约束、删约束）",
        "第四步：理解DROP的CASCADE和RESTRICT选项",
        "第五步：了解索引和视图的创建与删除"
    ],
    "tips": [
        "DDL语句通常自动提交事务，执行后不能回滚",
        "CHAR(n)是定长字符串，不足补空格；VARCHAR(n)是变长字符串，更节省空间",
        "主码约束自动创建唯一索引，外码约束可以提高连接查询效率",
        "索引不是越多越好，过多索引会降低插入、删除、更新的性能",
        "DROP TABLE是危险操作，会删除表中所有数据和结构"
    ],
    "faq": [
        {
            "question": "CHAR和VARCHAR有什么区别？",
            "answer": "CHAR(n)是定长字符串，长度固定为n，不足的用空格填充，查询时会自动去掉尾部空格。VARCHAR(n)是变长字符串，实际长度等于存储的字符串长度，最多不超过n。CHAR适合长度固定的字段（如性别、邮编），VARCHAR适合长度变化大的字段（如姓名、地址）。CHAR查询速度略快但浪费空间，VARCHAR节省空间但查询稍慢。"
        },
        {
            "question": "DROP TABLE的CASCADE和RESTRICT有什么区别？",
            "answer": "CASCADE（级联）：删除表时，同时删除依赖于该表的所有对象，如视图、约束、索引等。RESTRICT（限制）：如果该表被其他对象引用（如视图、外码约束），则拒绝删除。MySQL默认行为类似CASCADE（会自动删除外码约束和索引），PostgreSQL和SQL Server需要显式指定。"
        },
        {
            "question": "什么时候应该创建索引？",
            "answer": "应创建索引的情况：1）经常作为查询条件的列（WHERE子句中的列）；2）经常用于连接的列（JOIN条件中的列）；3）经常需要排序的列（ORDER BY中的列）；4）经常需要分组的列（GROUP BY中的列）；5）取值范围广且选择性高的列。不应创建索引的情况：1）数据量小的表；2）经常需要插入、删除、更新的表；3）取值范围小的列（如性别只有男女）；4）TEXT、BLOB等大字段列。"
        },
        {
            "question": "ALTER TABLE ADD COLUMN和DROP COLUMN有什么注意事项？",
            "answer": "ADD COLUMN：新增列时，表中已有行的该列值为NULL（或DEFAULT指定的默认值）。如果新增列有NOT NULL约束，必须指定DEFAULT值，否则已有行无法满足约束。DROP COLUMN：删除列会导致该列数据丢失，且如果该列被视图、约束、索引引用，需要先删除这些依赖对象。修改列的数据类型可能导致数据截断或转换失败，需谨慎操作。"
        }
    ]
}

ENRICHMENTS[12] = {
    "detail_content": (
        "SQL的数据操纵语言（DML）中最核心的是查询操作，使用SELECT语句。"
        "SELECT语句是SQL中功能最强大、使用最频繁的语句，用于从数据库中检索数据。\n\n"
        "【SELECT语句的基本语法】\n"
        "SELECT [ALL | DISTINCT] <目标列表达式> [, ...]\n"
        "FROM <表名或视图名> [, ...]\n"
        "[WHERE <条件表达式>]\n"
        "[GROUP BY <列名1> [HAVING <条件表达式>]]\n"
        "[ORDER BY <列名2> [ASC | DESC]];\n\n"
        "【各子句详解】\n"
        "1. SELECT子句：指定要查询的列。可以是列名、表达式、聚合函数。\n"
        "   - SELECT * 表示查询所有列\n"
        "   - DISTINCT 表示去除重复行\n"
        "   - 可以为列指定别名：SELECT 姓名 AS name FROM 学生\n"
        "   - 可以使用表达式：SELECT 姓名, 年龄+1 AS 明年年龄 FROM 学生\n\n"
        "2. FROM子句：指定查询的数据源（表或视图），可以是单表或多表。\n\n"
        "3. WHERE子句：指定查询条件，筛选满足条件的行。\n"
        "   - 比较运算符：=, >, <, >=, <=, !=, <>\n"
        "   - 范围查询：BETWEEN ... AND ...\n"
        "   - 集合查询：IN (值1, 值2, ...)\n"
        "   - 模糊查询：LIKE '模式'（%匹配任意字符串，_匹配单个字符）\n"
        "   - 空值判断：IS NULL / IS NOT NULL\n"
        "   - 逻辑运算符：AND, OR, NOT\n\n"
        "4. GROUP BY子句：按指定列分组，将相同值的行分为一组。通常与聚合函数配合使用。\n"
        "   HAVING子句：对分组后的结果进行筛选，必须与GROUP BY配合使用。\n\n"
        "5. ORDER BY子句：对查询结果排序。ASC升序（默认），DESC降序。可以按多列排序。\n\n"
        "【常用聚合函数】\n"
        "COUNT(*)：统计元组个数\n"
        "COUNT(列名)：统计该列非空值的个数\n"
        "SUM(列名)：求和（数值型）\n"
        "AVG(列名)：求平均值（数值型）\n"
        "MAX(列名)：求最大值\n"
        "MIN(列名)：求最小值\n\n"
        "【多表连接查询】\n"
        "当需要从多个表中查询数据时，需要使用连接：\n"
        "1. 等值连接：在WHERE子句中用'='指定连接条件\n"
        "   SELECT 学生.姓名, 选课.成绩 FROM 学生, 选课 WHERE 学生.学号=选课.学号;\n"
        "2. 自身连接：表与自身连接，需要使用别名\n"
        "3. 外连接：LEFT JOIN / RIGHT JOIN / FULL JOIN\n\n"
        "【查询执行顺序】\n"
        "SQL语句的逻辑执行顺序：FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY。"
        "注意：WHERE在分组前过滤行，HAVING在分组后过滤组。"
    ),
    "key_points": [
        "SELECT基本结构：SELECT列 FROM表 WHERE条件 GROUP BY分组 HAVING分组筛选 ORDER BY排序",
        "WHERE子句：行级过滤，支持比较、范围(BETWEEN)、集合(IN)、模糊(LIKE)、空值(IS NULL)",
        "LIKE通配符：%匹配任意长度字符串，_匹配单个字符",
        "聚合函数：COUNT/SUM/AVG/MAX/MIN，与GROUP BY配合使用",
        "执行顺序：FROM→WHERE→GROUP BY→HAVING→SELECT→ORDER BY"
    ],
    "learning_steps": [
        "第一步：掌握SELECT基本语法结构，理解各子句的作用",
        "第二步：熟练使用WHERE子句的各种条件（比较、范围、集合、模糊、空值）",
        "第三步：掌握聚合函数的使用，理解GROUP BY和HAVING的区别",
        "第四步：掌握多表连接查询（等值连接、外连接）",
        "第五步：理解查询的逻辑执行顺序，特别是WHERE和HAVING的区别"
    ],
    "tips": [
        "WHERE在分组前过滤行，HAVING在分组后过滤组，两者不可混用",
        "LIKE中%和_是通配符，如果要匹配%和_本身需要用ESCAPE转义",
        "聚合函数不能出现在WHERE子句中，只能出现在SELECT和HAVING中",
        "ORDER BY是唯一可以使用SELECT中定义的别名的子句",
        "多表连接时，如果两个表有同名列，需要用表名.列名限定"
    ],
    "faq": [
        {
            "question": "WHERE和HAVING有什么区别？",
            "answer": "WHERE在分组之前对行进行过滤，HAVING在分组之后对组进行过滤。WHERE不能使用聚合函数，HAVING可以使用聚合函数。例如：SELECT 学号, AVG(成绩) FROM 选课 GROUP BY 学号 HAVING AVG(成绩)>80; 这里HAVING用于筛选平均成绩大于80的学生组。如果写成WHERE AVG(成绩)>80是错误的，因为WHERE执行时还没有分组，无法计算聚合函数。"
        },
        {
            "question": "DISTINCT和GROUP BY去重有什么区别？",
            "answer": "DISTINCT用于去除SELECT结果中的重复行，作用于所有查询列。GROUP BY用于分组，通常配合聚合函数使用。如果只是简单去重，DISTINCT更简洁：SELECT DISTINCT 系别 FROM 学生; 等价于 SELECT 系别 FROM 学生 GROUP BY 系别;。但GROUP BY可以配合聚合函数做统计，如统计每个系的学生数：SELECT 系别, COUNT(*) FROM 学生 GROUP BY 系别;。"
        },
        {
            "question": "内连接和外连接有什么区别？",
            "answer": "内连接（INNER JOIN）：只返回两个表中匹配的行，不匹配的行被丢弃。外连接（OUTER JOIN）：除了返回匹配行外，还返回不匹配的行，对应列填NULL。左外连接（LEFT JOIN）返回左表所有行；右外连接（RIGHT JOIN）返回右表所有行；全外连接（FULL JOIN）返回两个表所有行。例如，要查询所有学生及其选课情况（包括没选课的学生），需要用左外连接：SELECT 学生.姓名, 选课.课程号 FROM 学生 LEFT JOIN 选课 ON 学生.学号=选课.学号;"
        },
        {
            "question": "ORDER BY中可以使用列别名吗？",
            "answer": "可以。ORDER BY是SQL中唯一可以引用SELECT子句中定义的列别名的子句。例如：SELECT 姓名, 年龄*12 AS 月龄 FROM 学生 ORDER BY 月龄 DESC; 这是因为ORDER BY在逻辑执行顺序中位于SELECT之后，此时别名已经定义。其他子句（WHERE、GROUP BY、HAVING）都不能使用别名，因为它们在SELECT之前执行。"
        }
    ]
}

ENRICHMENTS[13] = {
    "detail_content": (
        "SQL的数据操纵语言（DML）除了查询（SELECT）外，还包括插入（INSERT）、更新（UPDATE）和删除（DELETE）三种操作。"
        "这三种操作用于修改数据库中的数据。\n\n"
        "【INSERT语句（插入数据）】\n"
        "INSERT语句用于向表中插入新的数据行。\n"
        "基本语法：\n"
        "INSERT INTO <表名> [(<列名1>, <列名2>, ...)] VALUES (<值1>, <值2>, ...);\n"
        "如果省略列名，则需要按表定义的列顺序给出所有列的值。\n\n"
        "示例：\n"
        "INSERT INTO 学生(学号, 姓名, 年龄, 系别) VALUES ('2024001', '张三', 20, '计算机系');\n\n"
        "插入子查询结果：\n"
        "INSERT INTO <表名> [(<列名>,...)] <子查询>;\n"
        "可以将查询结果批量插入到表中。\n\n"
        "【UPDATE语句（更新数据）】\n"
        "UPDATE语句用于修改表中已有的数据。\n"
        "基本语法：\n"
        "UPDATE <表名> SET <列名1>=<表达式1> [, <列名2>=<表达式2>, ...] [WHERE <条件>];\n"
        "如果省略WHERE子句，则更新表中所有行。\n\n"
        "示例：\n"
        "UPDATE 学生 SET 年龄=年龄+1 WHERE 学号='2024001';\n"
        "UPDATE 学生 SET 系别='信息学院' WHERE 系别='计算机系';\n\n"
        "【DELETE语句（删除数据）】\n"
        "DELETE语句用于删除表中的数据行。\n"
        "基本语法：\n"
        "DELETE FROM <表名> [WHERE <条件>];\n"
        "如果省略WHERE子句，则删除表中所有行（但表结构仍然存在）。\n\n"
        "示例：\n"
        "DELETE FROM 学生 WHERE 学号='2024001';\n\n"
        "【DELETE与DROP TABLE、TRUNCATE的区别】\n"
        "- DELETE：删除表中的数据行（可带WHERE条件），表结构保留，可以回滚（在事务中），会触发触发器，删除速度较慢。\n"
        "- TRUNCATE：清空表中所有数据，表结构保留，不能回滚，不触发触发器，速度快。\n"
        "- DROP TABLE：删除表（数据和结构都删除），不能回滚。\n\n"
        "【数据操作的事务控制】\n"
        "INSERT、UPDATE、DELETE操作都可以在事务中执行，可以回滚。"
        "通过BEGIN TRANSACTION、COMMIT、ROLLBACK来控制事务。"
        "在执行修改操作前，建议先使用SELECT验证条件是否正确，避免误操作。"
    ),
    "key_points": [
        "INSERT：插入单行数据或子查询结果，VALUES指定值",
        "UPDATE：SET列=值，WHERE指定条件，省略WHERE更新所有行",
        "DELETE：删除满足条件的行，省略WHERE删除所有行",
        "DELETE/TRUNCATE/DROP区别：DELETE可回滚可带条件，TRUNCATE快不可回滚，DROP删表",
        "数据修改操作建议先SELECT验证条件，再执行修改"
    ],
    "learning_steps": [
        "第一步：掌握INSERT语法——指定列名和对应的值，或插入子查询结果",
        "第二步：掌握UPDATE语法——SET子句修改列值，WHERE指定条件",
        "第三步：掌握DELETE语法——FROM表名，WHERE指定条件",
        "第四步：理解DELETE、TRUNCATE、DROP TABLE的区别",
        "第五步：理解事务控制在数据修改中的重要性"
    ],
    "tips": [
        "UPDATE和DELETE如果忘记加WHERE，会修改/删除所有行，务必小心",
        "执行修改前先SELECT验证条件，确认无误后再执行修改",
        "INSERT可以一次插入多行：VALUES (值1), (值2), ...",
        "UPDATE的SET子句中可以使用表达式，如 年龄=年龄+1",
        "在事务中执行修改操作，可以用ROLLBACK撤销误操作"
    ],
    "faq": [
        {
            "question": "DELETE和TRUNCATE有什么区别？",
            "answer": "主要区别：1）DELETE可以带WHERE条件删除部分行，TRUNCATE只能删除全部行；2）DELETE是DML，可以回滚，TRUNCATE是DDL（在大多数DBMS中），不能回滚；3）DELETE逐行删除，速度慢，会触发触发器；TRUNCATE一次性清空，速度快，不触发触发器；4）DELETE后自增列值不会重置，TRUNCATE会重置自增列；5）DELETE不会释放表占用的存储空间，TRUNCATE会释放。"
        },
        {
            "question": "INSERT可以一次插入多行数据吗？",
            "answer": "可以。在MySQL、PostgreSQL等现代DBMS中，INSERT支持一次插入多行：INSERT INTO 学生(学号,姓名) VALUES ('001','张三'), ('002','李四'), ('003','王五');。每行用括号括起来，行之间用逗号分隔。也可以用INSERT...SELECT语句将查询结果批量插入：INSERT INTO 新表 SELECT * FROM 旧表 WHERE 条件;。"
        },
        {
            "question": "UPDATE时如何引用表中其他列的值？",
            "answer": "UPDATE的SET子句中可以引用同一行的其他列。例如，将所有学生的年龄加1：UPDATE 学生 SET 年龄=年龄+1;。将学生的'年龄月份'更新为年龄乘以12：UPDATE 学生 SET 年龄月=年龄*12;。需要注意的是，SET子句中多个赋值是按从左到右顺序执行的，后面的赋值可以使用前面已更新的值。"
        },
        {
            "question": "如何安全地执行DELETE或UPDATE操作？",
            "answer": "安全操作建议：1）执行前先用SELECT语句验证WHERE条件，确保选中的行是正确的；2）在事务中执行，确认无误后再COMMIT，否则ROLLBACK；3）对于重要数据，操作前做好备份；4）避免在生产环境直接执行不带WHERE的UPDATE/DELETE；5）使用LIMIT限制（MySQL中）只修改一定数量的行；6）对于批量操作，可以分批执行，每批提交一次。"
        }
    ]
}

ENRICHMENTS[14] = {
    "detail_content": (
        "SQL的聚集函数（聚合函数）用于对一组值进行计算并返回单个值。"
        "分组查询（GROUP BY）用于将数据按某列分组，对每组分别进行统计。"
        "聚集函数和分组查询是SQL中数据统计分析的核心工具。\n\n"
        "【聚集函数】\n"
        "1. COUNT(*)：统计查询结果的行数。\n"
        "2. COUNT(列名)：统计指定列中非空值的行数。\n"
        "3. COUNT(DISTINCT 列名)：统计指定列中不同非空值的个数。\n"
        "4. SUM(列名)：计算指定列的总和（数值型）。\n"
        "5. AVG(列名)：计算指定列的平均值（数值型）。\n"
        "6. MAX(列名)：返回指定列的最大值。\n"
        "7. MIN(列名)：返回指定列的最小值。\n\n"
        "注意：\n"
        "- 除了COUNT(*)外，其他聚集函数在计算时都会忽略NULL值。\n"
        "- 聚集函数只能用在SELECT子句和HAVING子句中，不能用在WHERE子句中。\n"
        "- 可以使用DISTINCT关键字在聚集函数中去重：SUM(DISTINCT 列名)、COUNT(DISTINCT 列名)。\n\n"
        "【GROUP BY分组查询】\n"
        "GROUP BY子句将查询结果按指定的列进行分组，值相同的行分为一组。"
        "分组后，每个组可以使用聚集函数进行统计。\n\n"
        "语法：\n"
        "SELECT <分组列>, <聚集函数>\n"
        "FROM <表名>\n"
        "WHERE <条件>\n"
        "GROUP BY <分组列>\n"
        "[HAVING <分组条件>];\n\n"
        "规则：\n"
        "1. SELECT子句中出现的列，要么是GROUP BY中的列，要么是聚集函数的参数。\n"
        "2. WHERE子句在分组前过滤行，HAVING子句在分组后过滤组。\n"
        "3. GROUP BY可以按多列分组，多列值都相同的行分为一组。\n\n"
        "【HAVING子句】\n"
        "HAVING子句用于对分组后的结果进行筛选，必须与GROUP BY配合使用。"
        "HAVING子句中可以使用聚集函数，而WHERE子句中不能。\n\n"
        "示例：查询平均成绩大于80分的学生学号和平均成绩：\n"
        "SELECT 学号, AVG(成绩) AS 平均成绩\n"
        "FROM 选课\n"
        "GROUP BY 学号\n"
        "HAVING AVG(成绩) > 80;\n\n"
        "【GROUP BY的执行过程】\n"
        "1. 根据WHERE子句筛选出满足条件的行；\n"
        "2. 按GROUP BY指定的列对筛选后的行进行分组；\n"
        "3. 对每个组应用聚集函数，生成汇总结果；\n"
        "4. 根据HAVING子句筛选分组结果；\n"
        "5. 按ORDER BY排序（如果有）。\n\n"
        "【多列分组】\n"
        "GROUP BY可以按多列分组，如 GROUP BY 系别, 年级 表示按系别和年级的组合分组。"
        "只有系别和年级都相同的学生才分为同一组。"
    ),
    "key_points": [
        "聚集函数：COUNT/SUM/AVG/MAX/MIN，忽略NULL（COUNT(*)除外）",
        "GROUP BY：按列分组，SELECT列必须是分组列或聚集函数参数",
        "HAVING：分组后筛选，可使用聚集函数；WHERE是分组前筛选",
        "聚集函数只能出现在SELECT和HAVING中，不能出现在WHERE中",
        "多列分组：GROUP BY 列1,列2，按列值组合分组"
    ],
    "learning_steps": [
        "第一步：掌握5个聚集函数的用法，理解它们对NULL的处理",
        "第二步：理解GROUP BY的分组原理——相同值的行分为一组",
        "第三步：掌握GROUP BY的规则——SELECT列必须是分组列或聚集函数",
        "第四步：区分WHERE和HAVING——WHERE分组前过滤行，HAVING分组后过滤组",
        "第五步：练习多列分组和复杂的统计查询"
    ],
    "tips": [
        "COUNT(*)统计行数，COUNT(列名)统计非空行数，COUNT(DISTINCT列名)统计不同值数",
        "GROUP BY后SELECT中不能出现非分组列、非聚集函数的列",
        "HAVING可以使用聚集函数，WHERE不能——这是两者最核心的区别",
        "如果GROUP BY的列有NULL值，NULL会被分为一组",
        "ORDER BY可以使用聚集函数的别名"
    ],
    "faq": [
        {
            "question": "WHERE和HAVING到底有什么区别？",
            "answer": "核心区别在于执行时机不同：WHERE在GROUP BY之前执行，对原始行进行过滤，不能使用聚集函数；HAVING在GROUP BY之后执行，对分组后的结果进行过滤，可以使用聚集函数。简单记忆：WHERE过滤'行'，HAVING过滤'组'。例如，要查询'计算机系中平均成绩大于80的学生'，系别条件用WHERE（分组前过滤），平均成绩条件用HAVING（分组后过滤）：SELECT 学号, AVG(成绩) FROM 选课 WHERE 学号 IN (SELECT 学号 FROM 学生 WHERE 系别='计算机系') GROUP BY 学号 HAVING AVG(成绩)>80;"
        },
        {
            "question": "为什么GROUP BY后SELECT不能出现非分组列？",
            "answer": "因为GROUP BY后，每组只返回一行结果。如果SELECT中出现了非分组列（且不在聚集函数中），DBMS不知道该返回该列的哪个值（因为一组中该列可能有多个不同的值）。例如，按系别分组后，SELECT 系别, 姓名 FROM 学生 GROUP BY 系别; 每个系有多个学生，'姓名'该返回哪个？SQL标准不允许这种写法（MySQL在某些配置下允许，但返回的值不确定）。正确做法是：SELECT 系别, COUNT(*) FROM 学生 GROUP BY 系别;"
        },
        {
            "question": "聚集函数遇到NULL值怎么处理？",
            "answer": "除了COUNT(*)外，所有聚集函数在计算时都会忽略NULL值。例如：SUM(成绩)会跳过成绩为NULL的行；AVG(成绩)计算时也会忽略NULL，分母是非空成绩的个数；MAX(成绩)和MIN(成绩)也会忽略NULL。COUNT(列名)统计的是非空值的行数。如果想将NULL视为0参与计算，可以使用COALESCE(列名, 0)或IFNULL(列名, 0)函数。"
        },
        {
            "question": "可以同时使用WHERE和HAVING吗？",
            "answer": "可以，而且经常需要同时使用。WHERE用于分组前的行级过滤，HAVING用于分组后的组级过滤。例如，查询'计算机系中平均成绩大于80的学生学号和平均成绩'：SELECT 学号, AVG(成绩) FROM 选课 WHERE 课程号 IN (SELECT 课程号 FROM 课程 WHERE 系别='计算机系') GROUP BY 学号 HAVING AVG(成绩)>80; 这里WHERE过滤了课程范围，HAVING过滤了平均成绩。"
        }
    ]
}

ENRICHMENTS[15] = {
    "detail_content": (
        "SQL的嵌套查询（子查询）和集合运算是实现复杂查询的重要手段。"
        "嵌套查询是指在一个查询的WHERE或HAVING子句中嵌入另一个SELECT查询。"
        "集合运算用于合并多个查询的结果。\n\n"
        "【嵌套查询（子查询）】\n"
        "嵌套查询中，外层查询称为父查询或外层查询，内层查询称为子查询。\n"
        "子查询可以分为相关子查询和不相关子查询。\n\n"
        "1. 不相关子查询：子查询的查询条件不依赖于父查询，可以独立执行。"
        "子查询的结果作为父查询的条件。\n"
        "示例：查询与'张三'在同一个系的学生：\n"
        "SELECT * FROM 学生 WHERE 系别 = (SELECT 系别 FROM 学生 WHERE 姓名='张三');\n\n"
        "2. 相关子查询：子查询的查询条件依赖于父查询的某个属性值。"
        "子查询需要针对父查询的每一行重复执行。\n"
        "示例：查询每个学生中成绩高于该学生平均成绩的选课记录：\n"
        "SELECT * FROM 选课 SC1 WHERE 成绩 > (SELECT AVG(成绩) FROM 选课 SC2 WHERE SC2.学号=SC1.学号);\n\n"
        "【带有IN的子查询】\n"
        "当子查询的结果是一个集合时，用IN或NOT IN判断是否属于该集合。\n"
        "示例：查询选修了'数据库'课程的学生姓名：\n"
        "SELECT 姓名 FROM 学生 WHERE 学号 IN (SELECT 学号 FROM 选课 WHERE 课程号 IN (SELECT 课程号 FROM 课程 WHERE 课程名='数据库'));\n\n"
        "【带有比较运算符的子查询】\n"
        "当子查询返回单个值时，可以用比较运算符（=, >, <, >=, <=, !=）。\n"
        "如果子查询返回多个值，需要配合ANY或ALL使用。\n"
        "- ANY：表示满足子查询结果中的任意一个值。如 >ANY(子查询) 表示大于子查询结果中的最小值。\n"
        "- ALL：表示满足子查询结果中的所有值。如 >ALL(子查询) 表示大于子查询结果中的最大值。\n\n"
        "【带有EXISTS的子查询】\n"
        "EXISTS用于判断子查询是否有结果返回（存在性判断）。\n"
        "EXISTS子查询不返回数据，只返回TRUE或FALSE。\n"
        "示例：查询选修了课程号为'C1'的学生姓名：\n"
        "SELECT 姓名 FROM 学生 WHERE EXISTS (SELECT * FROM 选课 WHERE 选课.学号=学生.学号 AND 课程号='C1');\n"
        "NOT EXISTS用于判断子查询没有结果。\n\n"
        "【集合运算】\n"
        "SQL提供了三种集合运算：UNION（并）、INTERSECT（交）、EXCEPT/MINUS（差）。\n"
        "使用集合运算的前提是：各查询结果的列数相同，对应列的数据类型兼容。\n\n"
        "1. UNION（并运算）：合并两个查询结果，自动去重。\n"
        "   SELECT 学号 FROM 选课 WHERE 课程号='C1'\n"
        "   UNION\n"
        "   SELECT 学号 FROM 选课 WHERE 课程号='C2';\n"
        "   UNION ALL不去重，效率更高。\n\n"
        "2. INTERSECT（交运算）：返回两个查询结果的公共部分。\n"
        "   SELECT 学号 FROM 选课 WHERE 课程号='C1'\n"
        "   INTERSECT\n"
        "   SELECT 学号 FROM 选课 WHERE 课程号='C2';\n\n"
        "3. EXCEPT/MINUS（差运算）：返回在第一个查询结果中但不在第二个查询结果中的部分。\n"
        "   SELECT 学号 FROM 选课 WHERE 课程号='C1'\n"
        "   EXCEPT\n"
        "   SELECT 学号 FROM 选课 WHERE 课程号='C2';"
    ),
    "key_points": [
        "嵌套查询分两类：不相关子查询（独立执行）和相关子查询（依赖父查询）",
        "IN子查询：判断是否在子查询结果集合中",
        "比较运算符+ANY/ALL：ANY=任一，ALL=所有",
        "EXISTS子查询：存在性判断，只返回TRUE/FALSE，常用于相关子查询",
        "集合运算：UNION(并)、INTERSECT(交)、EXCEPT(差)，要求列数和类型兼容"
    ],
    "learning_steps": [
        "第一步：理解嵌套查询的结构——父查询+子查询，子查询用括号括起来",
        "第二步：区分不相关子查询和相关子查询，理解执行顺序的差异",
        "第三步：掌握IN、比较运算符、EXISTS三种子查询形式",
        "第四步：理解ANY和ALL的含义——ANY=大于最小，ALL=大于最大",
        "第五步：掌握三种集合运算（UNION/INTERSECT/EXCEPT）及其去重行为"
    ],
    "tips": [
        "不相关子查询只执行一次，相关子查询对父查询每行都执行一次，效率较低",
        "EXISTS比IN在某些情况下更高效，特别是子查询结果集较大时",
        "UNION会自动去重，UNION ALL不去重效率更高，需要去重时才用UNION",
        "比较运算符+子查询要求子查询返回单个值，多值时用ANY/ALL",
        "EXISTS子查询中SELECT的内容不重要，通常写SELECT *或SELECT 1"
    ],
    "faq": [
        {
            "question": "相关子查询和不相关子查询有什么区别？",
            "answer": "不相关子查询：子查询的执行不依赖父查询，可以独立执行，只执行一次，结果传给父查询。效率较高。相关子查询：子查询的执行依赖父查询的当前行，需要为父查询的每一行执行一次子查询。效率较低。例如，'查询成绩大于该学生平均成绩的选课记录'是相关子查询（子查询中用到了父查询的学号），而'查询计算机系的所有学生'是不相关子查询（子查询可独立执行）。"
        },
        {
            "question": "IN和EXISTS子查询有什么区别？",
            "answer": "IN子查询：先执行子查询得到结果集，然后判断父查询的行是否在结果集中。适合子查询结果集较小的情况。EXISTS子查询：对父查询的每一行，执行子查询判断是否有结果返回。适合子查询结果集较大但有索引的情况。一般来说，当子查询结果集大时EXISTS更高效，结果集小时IN更高效。NOT EXISTS和NOT IN的区别更大：NOT IN中子查询结果有NULL时会返回空结果，NOT EXISTS不会有这个问题。"
        },
        {
            "question": ">ANY和>ALL分别是什么意思？",
            "answer": ">ANY(子查询)：大于子查询结果中的'任意一个'，即大于最小值。例如，>ANY(1,2,3)等价于>1。>ALL(子查询)：大于子查询结果中的'所有'，即大于最大值。例如，>ALL(1,2,3)等价于>3。类似地，<ANY等价于<最大值，<ALL等价于<最小值。ANY和ALL可以与各种比较运算符配合使用。"
        },
        {
            "question": "UNION和JOIN有什么区别？",
            "answer": "UNION是纵向合并，将两个查询结果的'行'合并在一起，要求列数和类型兼容。JOIN是横向合并，将两个表的'列'拼接在一起，通过连接条件关联。UNION增加行数，JOIN增加列数。例如，查询选修了C1或C2的学生用UNION（合并两个结果集的行）；查询学生姓名及其课程成绩用JOIN（拼接学生表和选课表的列）。"
        }
    ]
}

ENRICHMENTS[16] = {
    "detail_content": (
        "视图（View）是从一个或几个基本表（或视图）导出的表。"
        "视图是虚表，数据库中只存放视图的定义，而不存放视图对应的数据。"
        "视图一经定义，就可以和基本表一样被查询、删除，也可以在视图上再定义视图。\n\n"
        "【视图的定义】\n"
        "语法：CREATE VIEW <视图名> [(<列名>,...)] AS <子查询> [WITH CHECK OPTION];\n\n"
        "说明：\n"
        "- 子查询可以是任意的SELECT语句，但通常不允许包含ORDER BY子句和DISTINCT短语。\n"
        "- WITH CHECK OPTION表示对视图进行UPDATE、INSERT、DELETE操作时，要保证操作的行满足视图定义中的条件。\n"
        "- 如果不指定列名，视图的列名由子查询的SELECT子句决定。\n\n"
        "示例：建立计算机系学生的视图：\n"
        "CREATE VIEW CS_Student AS SELECT 学号, 姓名, 年龄 FROM 学生 WHERE 系别='计算机系';\n\n"
        "【视图的查询】\n"
        "对视图的查询与对基本表的查询完全相同。\n"
        "DBMS执行对视图的查询时，先将视图定义与用户查询合并，转换为对基本表的查询，然后执行。"
        "这个过程称为'视图消解'。\n\n"
        "示例：SELECT * FROM CS_Student WHERE 年龄<20;\n"
        "会被转换为：SELECT * FROM 学生 WHERE 系别='计算机系' AND 年龄<20;\n\n"
        "【视图的更新】\n"
        "视图的更新（INSERT、UPDATE、DELETE）最终要转换为对基本表的更新。\n"
        "但并非所有视图都可以更新，只有'行列子集视图'可以更新。\n"
        "行列子集视图：从单个基本表导出，保留了主码，且只做了简单的行选择和列投影。\n\n"
        "不可更新的视图：\n"
        "- 由两个以上基本表导出的视图；\n"
        "- 包含聚集函数、GROUP BY、DISTINCT的视图；\n"
        "- 包含子查询的视图；\n"
        "- 不包含基本表主码的视图。\n\n"
        "【视图的删除】\n"
        "DROP VIEW <视图名> [CASCADE];\n"
        "CASCADE表示级联删除该视图及基于该视图的其他视图。\n\n"
        "【视图的作用】\n"
        "1. 简化用户操作：将复杂的查询封装为视图，用户只需查询视图即可。\n"
        "2. 使用户能以多种角度看待同一数据：不同视图提供不同的数据视角。\n"
        "3. 对重构数据库提供一定程度的逻辑独立性：基本表结构改变时，通过视图可以保持应用程序不变。\n"
        "4. 提供安全保护：通过视图只向用户展示授权的数据，隐藏敏感数据。"
    ),
    "key_points": [
        "视图是虚表，只存定义不存数据，数据来自基本表",
        "CREATE VIEW ... AS SELECT ... 定义视图，WITH CHECK OPTION保证更新满足条件",
        "行列子集视图可更新（单表+主码+简单选择投影）",
        "视图查询通过'视图消解'转换为基本表查询",
        "视图作用：简化操作、多角度、逻辑独立性、安全保护"
    ],
    "learning_steps": [
        "第一步：理解视图的本质——虚表，只存定义不存数据",
        "第二步：掌握CREATE VIEW语法，理解WITH CHECK OPTION的作用",
        "第三步：理解视图查询的'视图消解'过程",
        "第四步：掌握可更新视图的条件（行列子集视图）",
        "第五步：理解视图的四大作用"
    ],
    "tips": [
        "视图本身不存储数据，查询视图实际是查询基本表",
        "WITH CHECK OPTION确保通过视图插入/更新的数据满足视图的WHERE条件",
        "包含GROUP BY、聚集函数、DISTINCT的视图不能更新",
        "视图可以基于其他视图定义，形成视图的层次结构",
        "视图是实现数据库安全的重要手段，通过视图限制用户可见的数据范围"
    ],
    "faq": [
        {
            "question": "视图和基本表有什么区别？",
            "answer": "基本表是实际存储数据的表，数据物理存储在磁盘上。视图是从基本表导出的虚表，数据库中只存储视图的定义（SELECT语句），不存储视图对应的数据。对视图的查询会被转换为对基本表的查询。对视图的更新（插入、修改、删除）只有在满足'行列子集视图'条件时才能转换为对基本表的更新，否则不允许更新。"
        },
        {
            "question": "什么是'视图消解'？",
            "answer": "视图消解（View Resolution）是DBMS处理视图查询的过程：1）将用户对视图的查询与视图的定义（子查询）进行合并；2）将合并后的查询转换为对基本表的查询；3）执行转换后的查询。例如，视图CS_Student定义为SELECT 学号,姓名 FROM 学生 WHERE 系别='计算机系'，查询SELECT * FROM CS_Student WHERE 年龄<20会被消解为SELECT 学号,姓名 FROM 学生 WHERE 系别='计算机系' AND 年龄<20。"
        },
        {
            "question": "为什么有些视图不能更新？",
            "answer": "因为视图更新需要能唯一地转换为对基本表的更新。行列子集视图（从单个基本表导出，保留主码，只做简单选择和投影）可以更新，因为视图的每一行对应基本表的一行。但包含聚集函数、GROUP BY、DISTINCT、多表连接的视图，其行无法唯一对应基本表的某一行，因此无法确定如何更新基本表。例如，按系别分组统计人数的视图，无法通过修改视图来修改学生表的数据。"
        },
        {
            "question": "视图如何提供安全保护？",
            "answer": "视图可以限制用户只能看到和操作授权的数据。例如，学生表包含学号、姓名、成绩、家庭住址、电话等信息。可以为教务人员创建只包含学号、姓名、成绩的视图，为辅导员创建包含学号、姓名、家庭住址、电话的视图。用户只能通过视图访问数据，无法直接访问基本表，从而隐藏了敏感信息。配合GRANT语句授予视图的查询权限而不授予基本表的权限，可以实现细粒度的安全控制。"
        }
    ]
}

ENRICHMENTS[17] = {
    "detail_content": (
        "存储过程（Stored Procedure）和触发器（Trigger）是数据库中用于实现复杂业务逻辑和数据完整性的重要对象。\n\n"
        "【存储过程】\n"
        "存储过程是一组为了完成特定功能的SQL语句集合，经编译后存储在数据库中。"
        "用户通过指定存储过程的名字并给出参数来执行它。\n\n"
        "存储过程的特点：\n"
        "1. 预编译：存储过程在创建时编译，执行时不需要重新编译，执行效率高。\n"
        "2. 封装性：将复杂的业务逻辑封装在存储过程中，对外只暴露接口。\n"
        "3. 可重用：存储过程可以被多次调用，避免重复编写代码。\n"
        "4. 减少网络流量：存储过程在服务器端执行，客户端只需传递参数和接收结果。\n"
        "5. 安全性：可以通过权限控制，只允许用户执行特定的存储过程。\n\n"
        "创建存储过程（MySQL语法）：\n"
        "CREATE PROCEDURE 过程名([IN|OUT|INOUT] 参数名 数据类型, ...)\n"
        "BEGIN\n"
        "    -- SQL语句\n"
        "END;\n"
        "\n"
        "调用存储过程：CALL 过程名(参数);\n"
        "删除存储过程：DROP PROCEDURE 过程名;\n\n"
        "【触发器】\n"
        "触发器是用户定义在关系表上的一类由事件驱动的特殊过程。"
        "当对表进行INSERT、UPDATE、DELETE操作时，触发器会自动执行。"
        "触发器不能被直接调用，只能由事件触发。\n\n"
        "触发器的类型：\n"
        "1. 按触发时机：BEFORE触发器（操作前执行）、AFTER触发器（操作后执行）。\n"
        "2. 按触发事件：INSERT触发器、UPDATE触发器、DELETE触发器。\n\n"
        "创建触发器（MySQL语法）：\n"
        "CREATE TRIGGER 触发器名\n"
        "{BEFORE|AFTER} {INSERT|UPDATE|DELETE}\n"
        "ON 表名 FOR EACH ROW\n"
        "BEGIN\n"
        "    -- SQL语句\n"
        "END;\n\n"
        "在触发器中可以使用OLD和NEW引用数据：\n"
        "- OLD：操作前的行数据（DELETE和UPDATE中可用）\n"
        "- NEW：操作后的行数据（INSERT和UPDATE中可用）\n\n"
        "【触发器的应用场景】\n"
        "1. 复杂的完整性约束：实现CHECK约束无法表达的复杂业务规则。\n"
        "2. 级联更新：当一个表的数据变化时，自动更新其他表。\n"
        "3. 审计日志：记录数据的修改历史。\n"
        "4. 数据校验：在插入或更新前验证数据是否符合规则。\n"
        "5. 自动计算：自动更新统计字段。\n\n"
        "【存储过程与触发器的区别】\n"
        "1. 存储过程由用户显式调用，触发器由事件自动触发。\n"
        "2. 存储过程可以有参数和返回值，触发器不能有参数。\n"
        "3. 存储过程可以返回结果集，触发器不能返回结果。\n"
        "4. 存储过程用于封装业务逻辑，触发器用于维护数据完整性和一致性。"
    ),
    "key_points": [
        "存储过程：预编译的SQL语句集合，通过CALL调用，可带参数",
        "存储过程优点：预编译效率高、封装业务逻辑、减少网络流量、安全",
        "触发器：事件驱动的特殊过程，INSERT/UPDATE/DELETE时自动执行",
        "触发器类型：BEFORE/AFTER × INSERT/UPDATE/DELETE",
        "触发器中OLD引用旧数据，NEW引用新数据"
    ],
    "learning_steps": [
        "第一步：理解存储过程的概念——预编译的SQL语句集合，存在数据库中",
        "第二步：掌握存储过程的创建和调用语法（CREATE PROCEDURE、CALL）",
        "第三步：理解触发器的概念——事件驱动，自动执行",
        "第四步：掌握触发器的创建语法和触发时机（BEFORE/AFTER）",
        "第五步：理解OLD和NEW的用法，区分存储过程和触发器"
    ],
    "tips": [
        "存储过程在创建时编译，执行时不需要重新编译，效率高",
        "触发器不能直接调用，只能由INSERT/UPDATE/DELETE事件触发",
        "在触发器中，INSERT操作只有NEW，DELETE操作只有OLD，UPDATE操作两者都有",
        "存储过程可以嵌套调用，但触发器中调用存储过程要谨慎（可能导致递归）",
        "触发器会增加数据库操作的开销，不宜过多使用"
    ],
    "faq": [
        {
            "question": "存储过程和普通SQL语句有什么区别？",
            "answer": "存储过程是预编译的SQL语句集合，存储在数据库中，通过CALL调用。普通SQL语句每次执行都需要解析和编译。存储过程的优势：1）预编译，执行效率高；2）封装业务逻辑，减少重复代码；3）减少网络传输（只需传递参数和结果）；4）安全性好（可以只授予执行权限）。劣势：1）调试困难；2）移植性差（不同DBMS语法不同）；3）增加数据库服务器负载。"
        },
        {
            "question": "OLD和NEW在触发器中怎么用？",
            "answer": "OLD和NEW是触发器中的特殊变量，用于引用被操作行的数据。OLD引用操作前的行数据，NEW引用操作后的行数据。INSERT触发器：只有NEW（新插入的数据）。DELETE触发器：只有OLD（被删除的数据）。UPDATE触发器：OLD（修改前）和NEW（修改后）都有。例如，CREATE TRIGGER t BEFORE UPDATE ON 学生 FOR EACH ROW BEGIN SET NEW.年龄=OLD.年龄+1; END; 表示每次更新学生表时，自动将年龄加1。"
        },
        {
            "question": "触发器和CHECK约束有什么区别？",
            "answer": "CHECK约束用于简单的数据完整性检查（如年龄>0），在表定义中声明，由DBMS强制检查。触发器可以实现更复杂的业务逻辑（如跨表约束、级联操作、审计日志），功能更强大但也更复杂。一般来说，能用CHECK约束实现的就不要用触发器，因为CHECK约束更简单、性能更好、更可靠。只有当CHECK约束无法满足需求时（如涉及其他表、复杂计算），才使用触发器。"
        },
        {
            "question": "存储过程和函数有什么区别？",
            "answer": "存储过程（PROCEDURE）和函数（FUNCTION）都是预编译的SQL集合。区别：1）函数必须有返回值，存储过程可以没有返回值；2）函数只能返回单个值，存储过程可以通过OUT参数返回多个值或结果集；3）函数可以在SELECT语句中调用（像内置函数一样），存储过程必须用CALL语句调用；4）函数中不能有事务控制语句（COMMIT/ROLLBACK），存储过程可以。"
        }
    ]
}

print(f"第3章内容已加载，共 {len([k for k in ENRICHMENTS if 11<=k<=17])} 个知识点")
