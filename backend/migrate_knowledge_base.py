import pymysql
import json

conn = pymysql.connect(host='localhost', user='root', password='mysql', database='dbms_course_hub', charset='utf8mb4')
cursor = conn.cursor()

knowledge_base_data = {
    1: {
        'category': '基础概念',
        'detail_content': '数据库系统是由数据库、数据库管理系统（DBMS）、应用程序和数据库管理员组成的完整系统。数据库是长期存储在计算机内的有组织、可共享的数据集合；DBMS是管理数据库的软件，负责数据的存储、检索、更新和保护。',
        'key_points': ['数据库系统组成', '数据库定义', 'DBMS功能', '数据独立性', '数据共享'],
        'image_prompt': 'Database system architecture diagram showing DBMS, database, application programs, and users with arrows indicating data flow, technical illustration, clean design, blue and white color scheme',
        'video_script': '步骤1: 介绍数据库系统的组成部分\n步骤2: 展示数据库管理系统(DBMS)的核心地位\n步骤3: 演示数据从应用程序到数据库的流动过程\n步骤4: 说明数据独立性的概念\n步骤5: 总结数据库系统的优势'
    },
    2: {
        'category': '基础概念',
        'detail_content': '数据管理技术经历了三个阶段：人工管理阶段、文件系统阶段和数据库系统阶段。人工管理阶段数据不共享、冗余度大；文件系统阶段数据以文件形式存储，有一定独立性但仍有冗余；数据库系统阶段数据结构化、共享性高、冗余度低、独立性强。',
        'key_points': ['人工管理阶段', '文件系统阶段', '数据库系统阶段', '数据冗余', '数据独立性'],
        'image_prompt': 'Data management evolution timeline showing three stages: manual management, file system, and database system, with comparison charts, technical infographic style, professional design',
        'video_script': '步骤1: 介绍数据管理技术的发展历程\n步骤2: 对比人工管理阶段的特点\n步骤3: 分析文件系统阶段的局限性\n步骤4: 展示数据库系统阶段的优势\n步骤5: 总结三个阶段的关键特征'
    },
    3: {
        'category': '基础概念',
        'detail_content': '数据库管理系统（DBMS）的主要功能包括：数据定义、数据操纵、数据库运行管理、数据组织存储管理、数据库保护和数据库维护。DBMS通过数据语言（DDL、DML、DCL）实现对数据库的操作和管理。',
        'key_points': ['数据定义功能', '数据操纵功能', '运行管理', '存储管理', '数据库保护'],
        'image_prompt': 'DBMS functions diagram showing data definition, manipulation, security, concurrency control, recovery, and maintenance, technical flowchart, professional illustration',
        'video_script': '步骤1: 概述DBMS的核心功能\n步骤2: 介绍数据定义语言(DDL)\n步骤3: 演示数据操纵语言(DML)\n步骤4: 说明数据库保护机制\n步骤5: 总结DBMS的作用'
    },
    4: {
        'category': '关系模型',
        'detail_content': '关系模型是目前最流行的数据模型，它用二维表格来表示数据及数据之间的关系。关系模型的基本概念包括：关系（表）、元组（行）、属性（列）、域、键（主键、外键）。关系模型具有结构简单、易于理解、数据独立性高等优点。',
        'key_points': ['关系定义', '元组', '属性', '主键', '外键', '关系完整性'],
        'image_prompt': 'Relational model diagram showing table structure with rows and columns, primary key and foreign key relationships between tables, entity-relationship style, clean technical illustration',
        'video_script': '步骤1: 介绍关系模型的基本概念\n步骤2: 展示关系(表)的结构\n步骤3: 解释主键和外键的作用\n步骤4: 演示表之间的关联关系\n步骤5: 总结关系模型的优势'
    },
    5: {
        'category': '关系模型',
        'detail_content': '关系代数是一种抽象的查询语言，用对关系的运算来表达查询。基本运算包括：选择(σ)、投影(π)、笛卡尔积(×)、自然连接(⋈)、并(∪)、差(-)、交(∩)。关系代数是SQL的理论基础，理解关系代数有助于编写高效的SQL查询。',
        'key_points': ['选择运算', '投影运算', '笛卡尔积', '自然连接', '并运算', '差运算'],
        'image_prompt': 'Relational algebra operations flowchart showing selection, projection, Cartesian product, natural join, union, and difference operations, mathematical notation, educational illustration',
        'video_script': '步骤1: 介绍关系代数的概念\n步骤2: 演示选择运算(σ)\n步骤3: 演示投影运算(π)\n步骤4: 讲解自然连接运算(⋈)\n步骤5: 总结关系代数与SQL的关系'
    },
    6: {
        'category': '关系模型',
        'detail_content': '关系的完整性约束包括：实体完整性、参照完整性和用户定义完整性。实体完整性要求主键非空且唯一；参照完整性要求外键必须是被参照表主键的有效值或空值；用户定义完整性是根据应用需求定义的约束条件。',
        'key_points': ['实体完整性', '参照完整性', '用户定义完整性', '主键约束', '外键约束'],
        'image_prompt': 'Relational integrity constraints diagram showing entity integrity, referential integrity, and user-defined integrity rules, constraint symbols, educational illustration',
        'video_script': '步骤1: 介绍关系完整性的概念\n步骤2: 解释实体完整性规则\n步骤3: 说明参照完整性规则\n步骤4: 举例用户定义完整性\n步骤5: 总结完整性约束的作用'
    },
    7: {
        'category': 'SQL',
        'detail_content': 'SELECT语句是SQL中最常用的查询语句，用于从数据库中检索数据。基本语法包括：SELECT子句（指定列）、FROM子句（指定表）、WHERE子句（过滤条件）、ORDER BY子句（排序）、LIMIT子句（限制结果数量）。SELECT语句支持多种查询方式，包括简单查询、连接查询、子查询等。',
        'key_points': ['SELECT子句', 'FROM子句', 'WHERE子句', 'ORDER BY', 'LIMIT', 'DISTINCT'],
        'image_prompt': 'SQL SELECT statement syntax diagram showing SELECT, FROM, WHERE, ORDER BY clauses with examples, code visualization, educational infographic',
        'video_script': '步骤1: 介绍SELECT语句的基本结构\n步骤2: 演示简单查询\n步骤3: 添加WHERE条件过滤\n步骤4: 使用ORDER BY排序\n步骤5: 总结SELECT语句的用法'
    },
    8: {
        'category': 'SQL',
        'detail_content': 'WHERE子句用于过滤SELECT查询返回的数据，只返回满足条件的行。WHERE条件可以使用比较运算符(=, <, >, <=, >=, <>)、逻辑运算符(AND, OR, NOT)、范围运算符(BETWEEN)、列表运算符(IN)和模糊查询(LIKE)。合理使用WHERE条件可以减少返回的数据量，提高查询效率。',
        'key_points': ['比较运算符', '逻辑运算符', 'BETWEEN', 'IN', 'LIKE', 'IS NULL'],
        'image_prompt': 'SQL WHERE clause operators chart showing comparison operators, logical operators, BETWEEN, IN, LIKE with examples, reference card style, educational design',
        'video_script': '步骤1: 介绍WHERE子句的作用\n步骤2: 演示比较运算符\n步骤3: 使用逻辑运算符组合条件\n步骤4: 讲解LIKE模糊查询\n步骤5: 总结WHERE条件的优化'
    },
    9: {
        'category': 'SQL',
        'detail_content': 'GROUP BY子句用于将查询结果按指定列进行分组，通常与聚合函数一起使用。常用聚合函数包括：COUNT()、SUM()、AVG()、MAX()、MIN()。HAVING子句用于过滤分组后的结果，与WHERE不同，HAVING可以使用聚合函数。GROUP BY和HAVING的组合使用可以实现复杂的数据统计和分析。',
        'key_points': ['GROUP BY', '聚合函数', 'COUNT', 'SUM', 'AVG', 'HAVING'],
        'image_prompt': 'SQL GROUP BY and aggregation functions diagram showing data grouping process with COUNT, SUM, AVG, MAX, MIN, data visualization, educational illustration',
        'video_script': '步骤1: 介绍GROUP BY子句\n步骤2: 演示COUNT聚合函数\n步骤3: 使用SUM和AVG计算\n步骤4: 添加HAVING过滤分组\n步骤5: 总结分组查询的应用'
    },
    10: {
        'category': 'SQL',
        'detail_content': 'JOIN操作用于将两个或多个表中的数据合并在一起。常见的JOIN类型包括：INNER JOIN（内连接）、LEFT JOIN（左连接）、RIGHT JOIN（右连接）、FULL JOIN（全连接）、CROSS JOIN（笛卡尔积）。JOIN操作基于表之间的关联字段（通常是外键）进行匹配，是SQL中最强大的数据检索方式之一。',
        'key_points': ['INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN', 'ON条件', '自连接'],
        'image_prompt': 'SQL JOIN types Venn diagram showing INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN with shaded areas representing matched rows, educational infographic, clear visual comparison',
        'video_script': '步骤1: 介绍多表连接的概念\n步骤2: 演示INNER JOIN内连接\n步骤3: 讲解LEFT JOIN左连接\n步骤4: 对比RIGHT JOIN和FULL JOIN\n步骤5: 总结JOIN的应用场景'
    },
    11: {
        'category': '数据库设计',
        'detail_content': 'ER模型（实体-关系模型）是数据库设计的重要工具，用于描述现实世界中的实体、属性和实体之间的关系。ER图的基本组成包括：实体（矩形）、属性（椭圆）、关系（菱形）。ER模型设计遵循以下原则：确定实体、定义属性、建立关系、确定基数、规范化。',
        'key_points': ['实体', '属性', '关系', 'ER图', '基数约束', '弱实体'],
        'image_prompt': 'Entity-Relationship ER diagram template showing entities, attributes, and relationships with cardinality indicators, UML style, professional database design illustration',
        'video_script': '步骤1: 介绍ER模型的概念\n步骤2: 识别实体和属性\n步骤3: 建立实体之间的关系\n步骤4: 确定关系基数\n步骤5: 总结ER模型设计步骤'
    },
    12: {
        'category': '数据库设计',
        'detail_content': '关系模式规范化是将一个不合理的关系模式分解为若干合理关系模式的过程。规范化的目的是消除数据冗余、避免更新异常。常见的范式包括：第一范式(1NF)、第二范式(2NF)、第三范式(3NF)、BCNF、第四范式(4NF)。3NF是最常用的规范化标准，要求非主属性不传递依赖于主键。',
        'key_points': ['1NF', '2NF', '3NF', 'BCNF', '数据冗余', '更新异常'],
        'image_prompt': 'Database normalization levels flowchart showing 1NF, 2NF, 3NF, BCNF with transformation rules, step-by-step transformation, educational diagram',
        'video_script': '步骤1: 介绍规范化的目的\n步骤2: 讲解第一范式(1NF)\n步骤3: 讲解第二范式(2NF)\n步骤4: 讲解第三范式(3NF)\n步骤5: 总结规范化的好处'
    },
    13: {
        'category': '安全性',
        'detail_content': '数据库访问控制是保护数据库安全的重要手段，包括用户认证、权限管理和角色分配。MySQL提供了GRANT和REVOKE语句来管理用户权限。访问控制策略应遵循最小权限原则，即只授予用户完成工作所需的最小权限。常见的权限类型包括：SELECT、INSERT、UPDATE、DELETE、CREATE、DROP等。',
        'key_points': ['用户认证', '权限管理', 'GRANT', 'REVOKE', '角色', '最小权限'],
        'image_prompt': 'Database access control diagram showing authentication, authorization, permission levels, role-based access control, security architecture, professional infographic',
        'video_script': '步骤1: 介绍数据库安全性概念\n步骤2: 演示用户创建和认证\n步骤3: 讲解GRANT权限授予\n步骤4: 使用REVOKE撤销权限\n步骤5: 总结访问控制策略'
    },
    14: {
        'category': '安全性',
        'detail_content': '数据加密技术用于保护敏感数据在存储和传输过程中的安全。数据库加密包括：静态数据加密（存储加密）、传输加密（SSL/TLS）和字段级加密。MySQL支持SSL连接加密和AES加密函数。加密虽然提高了安全性，但会增加存储开销和查询性能开销，需要在安全性和性能之间做出权衡。',
        'key_points': ['静态加密', '传输加密', '字段级加密', 'SSL/TLS', 'AES', '加密性能'],
        'image_prompt': 'Data encryption layers diagram showing data at rest encryption, data in transit encryption, field-level encryption, security layers visualization, professional design',
        'video_script': '步骤1: 介绍数据加密的重要性\n步骤2: 讲解静态数据加密\n步骤3: 演示传输加密SSL/TLS\n步骤4: 说明字段级加密\n步骤5: 总结加密策略选择'
    },
    15: {
        'category': '查询优化',
        'detail_content': '查询优化器是数据库管理系统的核心组件，负责生成最优的执行计划。优化器分析SQL语句和统计信息，评估不同执行策略的成本，选择代价最小的执行计划。优化器的工作流程包括：解析SQL、生成逻辑计划、生成物理计划、选择最优计划。影响优化器决策的因素包括：表的大小、索引统计信息、可用内存等。',
        'key_points': ['查询优化器', '执行计划', '成本估算', '统计信息', '优化策略'],
        'image_prompt': 'Query optimizer workflow diagram showing SQL parsing, logical plan generation, physical plan generation, cost estimation, plan selection, technical flowchart',
        'video_script': '步骤1: 介绍查询优化器的作用\n步骤2: 演示SQL解析过程\n步骤3: 讲解执行计划生成\n步骤4: 说明成本估算方法\n步骤5: 总结优化器的决策因素'
    },
    16: {
        'category': '查询优化',
        'detail_content': '索引优化是提高查询性能的关键手段。创建合适的索引可以显著加快数据检索速度，但过多的索引会降低写入性能。索引优化的原则包括：为WHERE条件和JOIN条件创建索引、使用覆盖索引避免回表、遵循最左匹配原则、定期分析索引使用情况、删除冗余索引。常见的索引失效场景包括：在索引列上使用函数、参与运算、使用LIKE "%xxx"模糊查询。',
        'key_points': ['索引创建', '覆盖索引', '最左匹配', '索引失效', '索引维护'],
        'image_prompt': 'Index optimization techniques infographic showing index creation rules, covering index benefits, leftmost prefix matching, common index failure scenarios, educational guide',
        'video_script': '步骤1: 介绍索引优化的重要性\n步骤2: 讲解何时创建索引\n步骤3: 演示覆盖索引的优势\n步骤4: 说明索引失效场景\n步骤5: 总结索引优化策略'
    },
    17: {
        'category': '查询优化',
        'detail_content': '执行计划是数据库优化器生成的查询执行步骤说明。使用EXPLAIN命令可以查看执行计划，了解查询的执行方式。执行计划的关键信息包括：type（访问类型）、key（使用的索引）、rows（预计扫描行数）、Extra（额外信息）。分析执行计划是诊断查询性能问题的重要方法，通过分析可以发现全表扫描、文件排序、临时表等性能问题。',
        'key_points': ['EXPLAIN', 'type列', 'key列', 'rows列', 'Extra列', '性能诊断'],
        'image_prompt': 'EXPLAIN output analysis chart showing type hierarchy from ALL to const, key column interpretation, rows estimation, Extra flags meaning, educational reference card',
        'video_script': '步骤1: 介绍执行计划的作用\n步骤2: 演示EXPLAIN命令使用\n步骤3: 分析type访问类型\n步骤4: 解读Extra信息\n步骤5: 总结执行计划分析方法'
    },
    18: {
        'category': '查询优化',
        'detail_content': 'SQL语句优化是提高数据库性能的重要途径。常见的优化技巧包括：避免SELECT *、合理使用索引、优化JOIN顺序、使用LIMIT限制结果、避免子查询、优化GROUP BY、使用批量操作。优化SQL语句需要理解数据库的工作原理和查询优化器的行为，通过实践不断积累经验。',
        'key_points': ['避免SELECT*', '索引使用', 'JOIN优化', 'LIMIT优化', '批量操作'],
        'image_prompt': 'SQL optimization tips checklist showing best practices like avoiding SELECT star, using proper indexes, optimizing JOINs, LIMIT usage, educational infographic',
        'video_script': '步骤1: 介绍SQL优化的基本原则\n步骤2: 演示SELECT *的问题\n步骤3: 讲解JOIN顺序优化\n步骤4: 说明批量操作的优势\n步骤5: 总结SQL优化技巧'
    },
    19: {
        'category': '事务',
        'detail_content': '事务是数据库操作的基本单位，具有ACID四个特性：原子性(Atomicity)、一致性(Consistency)、隔离性(Isolation)、持久性(Durability)。原子性要求事务中的操作要么全部执行，要么全部不执行；一致性要求事务执行前后数据满足完整性约束；隔离性要求事务之间相互隔离；持久性要求事务提交后数据永久保存。',
        'key_points': ['原子性', '一致性', '隔离性', '持久性', '事务控制'],
        'image_prompt': 'ACID properties diagram showing Atomicity, Consistency, Isolation, Durability with icons and brief descriptions, transaction fundamentals, educational illustration',
        'video_script': '步骤1: 介绍事务的概念\n步骤2: 讲解原子性(Atomicity)\n步骤3: 讲解一致性(Consistency)\n步骤4: 讲解隔离性和持久性\n步骤5: 总结ACID特性的重要性'
    },
    20: {
        'category': '事务',
        'detail_content': '事务隔离级别是数据库系统为平衡并发性能和数据一致性而设置的不同隔离程度。MySQL InnoDB支持四个隔离级别：READ UNCOMMITTED（读取未提交）、READ COMMITTED（读取已提交）、REPEATABLE READ（可重复读）、SERIALIZABLE（串行化）。隔离级别越高，一致性越强，但并发性能越低。InnoDB默认使用REPEATABLE READ级别。',
        'key_points': ['READ UNCOMMITTED', 'READ COMMITTED', 'REPEATABLE READ', 'SERIALIZABLE', '隔离级别对比'],
        'image_prompt': 'Transaction isolation levels comparison chart showing four levels with allowed anomalies (dirty read, non-repeatable read, phantom read), matrix format, educational reference',
        'video_script': '步骤1: 介绍事务隔离级别的概念\n步骤2: 讲解READ UNCOMMITTED级别\n步骤3: 讲解READ COMMITTED级别\n步骤4: 讲解REPEATABLE READ和SERIALIZABLE\n步骤5: 总结隔离级别的选择'
    },
    21: {
        'category': '并发控制',
        'detail_content': '锁是数据库实现并发控制的基本机制。锁的类型包括：共享锁(S锁/读锁)和排他锁(X锁/写锁)。锁的粒度包括：表级锁、行级锁和页级锁。InnoDB使用行级锁，支持高并发。意向锁用于指示表中已有行级锁，包括意向共享锁(IS)和意向排他锁(IX)。间隙锁用于防止幻读，锁定索引间隙。',
        'key_points': ['共享锁', '排他锁', '行级锁', '表级锁', '意向锁', '间隙锁'],
        'image_prompt': 'Lock types and granularity diagram showing shared lock, exclusive lock, row-level lock, table-level lock, gap lock with lock compatibility matrix, technical illustration',
        'video_script': '步骤1: 介绍锁的基本概念\n步骤2: 讲解共享锁和排他锁\n步骤3: 对比行级锁和表级锁\n步骤4: 说明意向锁的作用\n步骤5: 总结锁的使用策略'
    },
    22: {
        'category': '并发控制',
        'detail_content': 'MVCC（多版本并发控制）是一种并发控制技术，通过维护数据的多个版本来实现非锁定读。MVCC的核心机制包括：undo日志（存储数据历史版本）、read view（决定可见版本）、事务ID（标记数据版本）。MVCC的优点是读不阻塞写、写不阻塞读，显著提高了并发性能。InnoDB通过MVCC实现REPEATABLE READ隔离级别。',
        'key_points': ['MVCC', 'undo日志', 'read view', '事务ID', '快照读', '当前读'],
        'image_prompt': 'MVCC multi-version concurrency control diagram showing multiple data versions, undo log chain, read view visibility determination, transaction IDs, technical illustration',
        'video_script': '步骤1: 介绍MVCC的概念\n步骤2: 讲解undo日志的作用\n步骤3: 演示read view的工作原理\n步骤4: 说明事务ID的作用\n步骤5: 总结MVCC的优势'
    },
    23: {
        'category': '并发控制',
        'detail_content': '死锁是指两个或多个事务互相等待对方释放锁而无法继续执行的状态。死锁发生需要四个必要条件：互斥条件、请求与保持条件、不剥夺条件、循环等待条件。MySQL InnoDB会自动检测死锁并回滚代价较小的事务。预防死锁的方法包括：按顺序获取锁、一次性获取所有锁、设置锁等待超时。',
        'key_points': ['死锁条件', '死锁检测', '死锁处理', '死锁预防', 'innodb_lock_wait_timeout'],
        'image_prompt': 'Deadlock scenario diagram showing two transactions waiting for each other\'s locks, circular dependency, four necessary conditions listed, educational illustration',
        'video_script': '步骤1: 介绍死锁的概念\n步骤2: 讲解死锁的四个条件\n步骤3: 演示死锁场景\n步骤4: 说明MySQL的死锁处理\n步骤5: 总结死锁预防策略'
    },
    24: {
        'category': '索引',
        'detail_content': 'B+树是一种平衡的多路搜索树，是数据库索引的主流数据结构。B+树的特点包括：所有数据存储在叶子节点、叶子节点形成双向链表、非叶子节点只存储索引键、高度平衡。B+树保证了O(log n)的查找效率，适合磁盘存储和范围查询。B+树的阶数通常为100-200，保证树的高度在2-4层。',
        'key_points': ['B+树结构', '叶子节点', '链表结构', '非叶子节点', '平衡特性'],
        'image_prompt': 'B+ tree data structure diagram showing internal nodes with index keys, leaf nodes with data and linked list pointers, balanced tree structure, technical illustration',
        'video_script': '步骤1: 介绍B+树的概念\n步骤2: 展示B+树的结构\n步骤3: 讲解叶子节点的特点\n步骤4: 演示查找过程\n步骤5: 总结B+树的优势'
    },
    25: {
        'category': '索引',
        'detail_content': 'B+树的插入和删除操作需要保持树的平衡。插入时，如果节点满了需要分裂：将节点分为两个，中间键上升到父节点。删除时，如果节点空了需要合并：与兄弟节点合并，父节点中的键下降。分裂和合并可能导致树的高度增加或减少。B+树的插入和删除复杂度均为O(log n)。',
        'key_points': ['节点分裂', '节点合并', '插入操作', '删除操作', '平衡维护'],
        'image_prompt': 'B+ tree insertion and deletion animation steps showing node split during insertion and node merge during deletion, step-by-step visualization, educational diagram',
        'video_script': '步骤1: 介绍B+树的插入操作\n步骤2: 演示节点分裂过程\n步骤3: 介绍B+树的删除操作\n步骤4: 演示节点合并过程\n步骤5: 总结B+树的平衡机制'
    },
    26: {
        'category': '索引',
        'detail_content': '聚集索引和非聚集索引是两种主要的索引类型。聚集索引的特点是数据按索引顺序存储，叶子节点包含完整的数据行，一张表只能有一个聚集索引。InnoDB的主键索引就是聚集索引。非聚集索引的叶子节点存储主键值，需要通过主键回表获取完整数据，一张表可以有多个非聚集索引。选择聚集索引键时应考虑唯一性、稳定性和递增性。',
        'key_points': ['聚集索引', '非聚集索引', '主键索引', '回表', '索引选择'],
        'image_prompt': 'Clustered vs non-clustered index comparison diagram showing clustered index with data in leaf nodes, non-clustered index with primary key in leaf nodes, clear visual distinction',
        'video_script': '步骤1: 介绍聚集索引的概念\n步骤2: 讲解非聚集索引\n步骤3: 对比两者的区别\n步骤4: 演示回表过程\n步骤5: 总结索引类型选择'
    },
    27: {
        'category': '索引',
        'detail_content': '覆盖索引是指查询所需的所有列都在索引中，可以避免回表操作，显著提高查询性能。索引下推(ICP)是在存储引擎层就过滤数据，减少回表次数。覆盖索引和索引下推是MySQL优化查询性能的重要技术。启用索引下推的参数是optimizer_switch="index_condition_pushdown=on"。',
        'key_points': ['覆盖索引', '回表', '索引下推', 'ICP', '查询优化'],
        'image_prompt': 'Covering index and index condition pushdown diagram showing how covering index avoids table lookup, ICP filters at storage engine level, performance comparison, educational illustration',
        'video_script': '步骤1: 介绍覆盖索引的概念\n步骤2: 演示覆盖索引的优势\n步骤3: 讲解索引下推(ICP)\n步骤4: 说明ICP的工作原理\n步骤5: 总结索引优化技巧'
    },
    28: {
        'category': '索引',
        'detail_content': '索引失效是指查询没有使用预期的索引，导致全表扫描或性能下降。常见的索引失效场景包括：在索引列上使用函数、索引列参与运算、使用LIKE "%xxx"模糊查询、类型转换、违反最左匹配原则、使用OR连接非索引列。避免索引失效的方法包括：避免在索引列使用函数、避免索引列参与运算、使用最左匹配、避免类型转换。',
        'key_points': ['函数操作', '运算操作', '模糊查询', '类型转换', '最左匹配', 'OR连接'],
        'image_prompt': 'Common index failure scenarios checklist with examples of each case, "DO NOT" patterns, educational warning card, clear visual presentation',
        'video_script': '步骤1: 介绍索引失效的概念\n步骤2: 演示函数操作导致失效\n步骤3: 讲解运算操作的影响\n步骤4: 说明模糊查询的注意事项\n步骤5: 总结避免索引失效的方法'
    },
    29: {
        'category': '安全性',
        'detail_content': '视图是从一个或多个表中导出的虚拟表，不存储数据，只是查询的定义。视图的主要作用包括：简化复杂查询、提供数据安全（限制用户访问特定数据）、提供逻辑独立性。视图可以更新，但有很多限制：不能有聚合函数、DISTINCT、GROUP BY、子查询等。物化视图会存储查询结果，定期刷新，适用于复杂查询的性能优化。',
        'key_points': ['视图定义', '视图优点', '视图更新', '物化视图', '安全应用'],
        'image_prompt': 'Database view concept diagram showing base tables, view as virtual table, security layer protecting sensitive data, educational illustration',
        'video_script': '步骤1: 介绍视图的概念\n步骤2: 演示视图的创建\n步骤3: 讲解视图的优点\n步骤4: 说明视图更新的限制\n步骤5: 总结视图的应用场景'
    },
    30: {
        'category': '安全性',
        'detail_content': '审计日志和数据备份是数据库安全的重要组成部分。审计日志记录数据库的操作历史，用于安全审计和故障排查。MySQL的二进制日志(binlog)主要用于数据恢复和主从复制。数据库备份类型包括：全量备份、增量备份、差异备份。备份策略需要考虑RTO（恢复时间目标）和RPO（恢复点目标），定期测试备份恢复过程。',
        'key_points': ['审计日志', 'binlog', '全量备份', '增量备份', 'RTO', 'RPO'],
        'image_prompt': 'Database backup and recovery strategy diagram showing full backup, incremental backup, log-based recovery, RTO and RPO indicators, professional infographic',
        'video_script': '步骤1: 介绍审计日志的作用\n步骤2: 讲解binlog的使用\n步骤3: 演示全量备份\n步骤4: 说明增量备份策略\n步骤5: 总结备份恢复最佳实践'
    }
}

for kp_id, data in knowledge_base_data.items():
    update_sql = """
    UPDATE knowledge_points 
    SET category = %s, detail_content = %s, key_points = %s, image_prompt = %s, video_script = %s, updated_at = NOW()
    WHERE id = %s
    """
    cursor.execute(update_sql, (
        data['category'],
        data['detail_content'],
        json.dumps(data['key_points']),
        data['image_prompt'],
        data['video_script'],
        kp_id
    ))

print(f"Updated {cursor.rowcount} knowledge points")
conn.commit()
conn.close()
print("Done!")
