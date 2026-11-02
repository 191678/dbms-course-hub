"""
Insert questions properly mapped to knowledge points.
"""
from app.database import get_db
from app.models import Question, KnowledgePoint
import json

db = next(get_db())

# Get all knowledge points grouped by chapter
kps = db.query(KnowledgePoint).order_by(KnowledgePoint.chapter_id, KnowledgePoint.order_index).all()
print(f"Total knowledge points: {len(kps)}")

# Build a mapping: for each chapter, list of (kp_id, content)
chapter_kps = {}
for kp in kps:
    if kp.chapter_id not in chapter_kps:
        chapter_kps[kp.chapter_id] = []
    chapter_kps[kp.chapter_id].append((kp.id, kp.content))

for ch_id, kp_list in chapter_kps.items():
    print(f"Chapter {ch_id}: {len(kp_list)} KPs")
    for kpid, kpcontent in kp_list[:3]:
        print(f"  {kpid}: {kpcontent[:50]}")

# Sample question templates by chapter
question_templates = {
    1: [  # 数据库系统概述
        ('easy', 'single', '数据管理技术经历了哪三个阶段？',
         json.dumps(['人工管理、文件系统、数据库系统', '手工操作、磁盘操作、网络操作', '单机、局域网、互联网', '低级、中级、高级']),
         'A', '数据管理技术经历了人工管理、文件系统和数据库系统三个阶段。'),
        ('easy', 'single', '数据库系统的核心是？',
         json.dumps(['数据库', '数据库管理系统', '操作系统', '应用程序']),
         'B', '数据库管理系统（DBMS）是数据库系统的核心软件。'),
        ('easy', 'single', '下列哪项不属于数据库系统的组成？',
         json.dumps(['数据库', '数据库管理系统', '应用程序', '编译器']),
         'D', '数据库系统由数据库、DBMS、应用程序和DBA组成，不包括编译器。'),
        ('medium', 'single', '数据模型的三个组成部分不包括？',
         json.dumps(['数据结构', '数据操作', '完整性约束', '数据存储']),
         'D', '数据模型由数据结构、数据操作和完整性约束三部分组成。'),
        ('medium', 'single', '数据库系统的三级模式结构是指？',
         json.dumps(['外模式、模式、内模式', '用户模式、系统模式、存储模式', '概念模式、逻辑模式、物理模式', '前端、后端、数据库']),
         'A', '三级模式结构包括外模式、模式（逻辑模式）和内模式（存储模式）。'),
        ('medium', 'multi', '数据库系统的组成包括？',
         json.dumps(['数据库', '数据库管理系统', '应用程序', '数据库管理员']),
         'ABCD', '数据库系统由数据库、DBMS、应用程序和DBA组成。'),
        ('hard', 'judge', '数据库的物理独立性是指用户应用程序与数据的物理存储结构无关。',
         None, '正确', '物理独立性确保用户应用程序与数据的物理存储结构变化无关。'),
        ('easy', 'single', 'DBMS中DDL的全称是？',
         json.dumps(['Data Definition Language', 'Data Description Language', 'Data Design Language', 'Data Development Language']),
         'A', 'DDL是Data Definition Language的缩写，即数据定义语言。'),
        ('medium', 'single', '数据库三级模式中，内模式改变时，外模式不变，这体现了？',
         json.dumps(['物理独立性', '逻辑独立性', '数据独立性', '一致性']),
         'A', '内模式改变而外模式不变是物理独立性的体现。'),
    ],
    2: [  # 关系数据库基础
        ('easy', 'single', '关系数据库中，表的行称为？',
         json.dumps(['元组', '属性', '字段', '记录']),
         'A', '在关系模型中，表的行称为元组。'),
        ('easy', 'single', '关系数据库中，表的列称为？',
         json.dumps(['元组', '属性', '记录', '行']),
         'B', '在关系模型中，表的列称为属性。'),
        ('medium', 'single', '关系的完整性约束不包括？',
         json.dumps(['实体完整性', '参照完整性', '用户定义的完整性', '数据完整性']),
         'D', '关系完整性包括实体完整性、参照完整性和用户定义的完整性。'),
        ('medium', 'single', '主键的特点是？',
         json.dumps(['唯一性', '非空性', '唯一性和非空性', '任意性']),
         'C', '主键必须同时满足唯一性和非空性。'),
        ('medium', 'multi', '关系代数的基本运算包括？',
         json.dumps(['选择', '投影', '并', '差']),
         'ABCD', '关系代数的基本运算包括选择、投影、并、差和笛卡尔积。'),
        ('hard', 'single', '下列哪个连接是自然连接？',
         json.dumps(['选择条件连接', '等值连接', '去除重复列的等值连接', '笛卡尔积']),
         'C', '自然连接是去除重复列的等值连接。'),
        ('easy', 'judge', '在关系中，同一列的数据类型必须相同。',
         None, '正确', '关系的每一列必须有相同的数据类型。'),
        ('medium', 'single', '实体完整性要求？',
         json.dumps(['主键不能为空', '外键不能为空', '属性不能为空', '所有字段不能为空']),
         'A', '实体完整性要求主键取值不能空。'),
        ('hard', 'single', '关系R和S的自然连接与等值连接的区别是？',
         json.dumps(['没有区别', '自然连接去除了重复的列', '等值连接去除了重复的行', '自然连接使用不同的操作符']),
         'B', '自然连接是等值连接中去除重复列的特殊情况。'),
    ],
    3: [  # SQL语言
        ('easy', 'single', 'SQL中用于查询数据的关键字是？',
         json.dumps(['SELECT', 'INSERT', 'UPDATE', 'DELETE']),
         'A', 'SELECT用于从数据库查询数据。'),
        ('easy', 'single', 'SQL中用于插入数据的关键字是？',
         json.dumps(['SELECT', 'INSERT', 'UPDATE', 'DELETE']),
         'B', 'INSERT用于插入新数据。'),
        ('medium', 'single', 'SQL中用于修改表结构的关键字是？',
         json.dumps(['MODIFY', 'ALTER', 'CHANGE', 'UPDATE']),
         'B', 'ALTER TABLE用于修改表结构。'),
        ('medium', 'single', 'WHERE子句的作用是？',
         json.dumps(['排序', '分组', '筛选', '连接']),
         'C', 'WHERE子句用于筛选满足条件的行。'),
        ('medium', 'single', 'GROUP BY子句的作用是？',
         json.dumps(['排序', '分组', '筛选', '连接']),
         'B', 'GROUP BY用于分组查询。'),
        ('medium', 'single', 'ORDER BY子句默认的排序方式是？',
         json.dumps(['升序', '降序', '随机', '自定义']),
         'A', 'ORDER BY默认按升序排列。'),
        ('easy', 'multi', '以下属于DDL语句的有？',
         json.dumps(['CREATE', 'ALTER', 'DROP', 'SELECT']),
         'ABC', 'CREATE、ALTER、DROP属于DDL，SELECT属于DML。'),
        ('medium', 'single', '以下哪个函数用于统计行数？',
         json.dumps(['SUM', 'COUNT', 'AVG', 'MAX']),
         'B', 'COUNT用于统计行数。'),
        ('medium', 'single', 'JOIN中默认的连接类型是？',
         json.dumps(['内连接', '左外连接', '右外连接', '全外连接']),
         'A', 'JOIN默认是INNER JOIN（内连接）。'),
        ('hard', 'single', '子查询的执行顺序是？',
         json.dumps(['先执行外层查询', '先执行内层查询', '同时执行', '随机执行']),
         'B', '子查询（内层查询）先执行，结果用于外层查询。'),
        ('easy', 'single', 'SQL中用于删除表的关键字是？',
         json.dumps(['DELETE', 'DROP', 'REMOVE', 'CLEAR']),
         'B', 'DROP TABLE用于删除整个表。'),
    ],
    4: [  # 数据库安全性
        ('easy', 'single', '数据库安全性的目标是？',
         json.dumps(['保护数据库免受各类威胁', '提高数据库性能', '增加数据冗余', '减少数据完整性']),
         'A', '数据库安全性的目标是保护数据库免受各类威胁。'),
        ('medium', 'single', '以下哪种不是常见的数据库安全威胁？',
         json.dumps(['非法访问', '数据泄露', '数据完整性破坏', '数据备份']),
         'D', '数据备份是安全措施，不是威胁。'),
        ('medium', 'multi', '数据库安全措施包括？',
         json.dumps(['用户认证', '访问控制', '数据加密', '审计']),
         'ABCD', '这些都是常见的数据库安全措施。'),
        ('hard', 'single', 'GRANT语句的作用是？',
         json.dumps(['授予权限', '撤销权限', '创建用户', '删除用户']),
         'A', 'GRANT用于授予用户权限。'),
        ('hard', 'single', 'REVOKE语句的作用是？',
         json.dumps(['授予权限', '撤销权限', '创建用户', '删除用户']),
         'B', 'REVOKE用于撤销用户权限。'),
        ('medium', 'single', '访问控制的三种策略不包括？',
         json.dumps(['自主访问控制(DAC)', '强制访问控制(MAC)', '角色访问控制(RBAC)', '自由访问控制(FAC)']),
         'D', 'DAC、MAC、RBAC是三种主要访问控制策略。'),
        ('easy', 'judge', '审计可以记录用户的数据库操作。',
         None, '正确', '审计可以追踪和记录用户的数据库操作。'),
    ],
    5: [  # 数据库完整性
        ('easy', 'single', '数据库完整性约束的类型不包括？',
         json.dumps(['实体完整性', '参照完整性', '用户定义的完整性', '系统完整性']),
         'D', '完整性约束包括实体完整性、参照完整性和用户定义的完整性。'),
        ('medium', 'single', 'CHECK约束的作用是？',
         json.dumps(['确保主键唯一', '确保列值满足特定条件', '建立外键关系', '加密数据']),
         'B', 'CHECK约束用于确保列值满足指定条件。'),
        ('medium', 'single', 'FOREIGN KEY约束用于？',
         json.dumps(['确保主键唯一', '建立表间关系', '检查列值范围', '加密数据']),
         'B', 'FOREIGN KEY用于建立表间的参照关系。'),
        ('medium', 'single', 'DEFAULT约束的作用是？',
         json.dumps(['设置列的默认值', '确保唯一性', '建立外键', '加密数据']),
         'A', 'DEFAULT约束为列设置默认值。'),
        ('hard', 'single', '以下哪种约束用于防止重复数据？',
         json.dumps(['UNIQUE', 'NOT NULL', 'DEFAULT', 'CHECK']),
         'A', 'UNIQUE约束确保列值唯一，防止重复。'),
        ('easy', 'judge', '实体完整性要求主键不能为空。',
         None, '正确', '实体完整性要求主键取值不能空。'),
        ('medium', 'single', 'NOT NULL约束的作用是？',
         json.dumps(['允许空值', '禁止空值', '设置默认值', '建立唯一约束']),
         'B', 'NOT NULL约束禁止列值为空。'),
    ],
    6: [  # 关系数据理论
        ('easy', 'single', '函数依赖的基本类型不包括？',
         json.dumps(['完全函数依赖', '部分函数依赖', '传递函数依赖', '直接函数依赖']),
         'D', '函数依赖包括完全、部分和传递函数依赖。'),
        ('medium', 'single', '第一范式(1NF)要求？',
         json.dumps(['属性不可再分', '消除部分依赖', '消除传递依赖', '消除冗余']),
         'A', '1NF要求属性不可再分，即每个属性都是原子的。'),
        ('medium', 'single', '第二范式(2NF)要求？',
         json.dumps(['属性不可再分', '消除非主属性对码的部分函数依赖', '消除传递依赖', '完全规范化']),
         'B', '2NF在1NF基础上消除非主属性对码的部分函数依赖。'),
        ('medium', 'single', '第三范式(3NF)要求？',
         json.dumps(['属性不可再分', '消除部分依赖', '消除非主属性对码的传递函数依赖', 'BCNF']),
         'C', '3NF在2NF基础上消除非主属性对码的传递函数依赖。'),
        ('hard', 'single', 'BCNF要求？',
         json.dumps(['每个决定因素都是候选码', '消除所有冗余', '属性都为主属性', '完全规范化']),
         'A', 'BCNF要求每个函数依赖的决定因素都是候选码。'),
        ('easy', 'judge', '函数依赖X→Y表示Y完全依赖于X。',
         None, '错误', 'X→Y仅表示Y函数依赖于X，不一定是完全的。'),
        ('medium', 'single', '候选码的定义是？',
         json.dumps(['能唯一标识元组的属性或属性组', '主键', '外键', '索引键']),
         'A', '候选码是能唯一标识元组的最小属性集。'),
        ('hard', 'single', 'Armstrong公理系统的基本规则不包括？',
         json.dumps(['自反律', '增广律', '传递律', '分配律']),
         'D', 'Armstrong公理的基本规则是自反律、增广律和传递律。'),
        ('easy', 'single', '属性集X的闭包X⁺是指？',
         json.dumps(['X的所有子集', '由X可以函数依赖推出的所有属性', 'X的超集', 'X的补集']),
         'B', 'X⁺是由X通过函数依赖推导出的所有属性的集合。'),
        ('medium', 'single', '模式分解的特性不包括？',
         json.dumps(['无损连接性', '保持函数依赖', '高安全性', '最小冗余']),
         'C', '模式分解应满足无损连接性和保持函数依赖。'),
    ],
    7: [  # 数据库设计
        ('easy', 'single', '数据库设计的六个阶段不包括？',
         json.dumps(['需求分析', '概念结构设计', '逻辑结构设计', '物理测试']),
         'D', '数据库设计分为需求分析、概念设计、逻辑设计、物理设计、实施和运行维护六个阶段。'),
        ('medium', 'single', 'ER模型中，实体间的联系不包括？',
         json.dumps(['一对一', '一对多', '多对多', '多对一']),
         'D', 'ER模型中联系包括1:1、1:n和m:n。'),
        ('medium', 'single', '把ER模型转换成关系模型时，m:n联系如何处理？',
         json.dumps(['转换为一个独立的关系', '合并到任一实体', '删除', '合并到主键']),
         'A', 'm:n联系需转换为独立的关系模式。'),
        ('easy', 'single', '概念结构设计的主要工具是？',
         json.dumps(['数据流图', 'ER图', '系统流程图', '程序流程图']),
         'B', 'ER图是概念结构设计的主要工具。'),
        ('medium', 'single', '逻辑结构设计的任务是？',
         json.dumps(['将概念模型转换为数据模型', '设计物理存储', '编写程序', '测试系统']),
         'A', '逻辑结构设计将概念模型转换为特定DBMS支持的数据模型。'),
        ('medium', 'single', '物理结构设计的内容包括？',
         json.dumps(['确定数据分布', '确定存储结构和存取方式', '确定表结构', '确定ER模型']),
         'B', '物理设计确定数据的存储结构和存取方式。'),
        ('easy', 'judge', 'ER模型是数据库概念设计的主要工具。',
         None, '正确', 'ER模型（实体-联系模型）是概念设计的主要工具。'),
        ('hard', 'single', '在ER模型中，属性的特性是？',
         json.dumps(['不可再分', '可以再分', '可以为空', '必须唯一']),
         'A', 'ER模型中的属性是原子的、不可再分的。'),
        ('medium', 'single', '将ER图转换为关系模式时，实体之间的1:n联系如何表示？',
         json.dumps(['在n端加入1端的主键作为外键', '在1端加入n端的主键', '创建新表', '合并为一个表']),
         'A', '1:n联系在n端加入1端实体的主键作为外键。'),
    ],
    8: [  # 数据库编程
        ('easy', 'single', '存储过程的特点是？',
         json.dumps(['存储在数据库中', '只能用Java编写', '不能接受参数', '只能查询数据']),
         'A', '存储过程是存储在数据库中的一组SQL语句。'),
        ('medium', 'single', '触发器的触发时机不包括？',
         json.dumps(['BEFORE', 'AFTER', 'INSTEAD OF', 'WHILE']),
         'D', '触发器的触发时机包括BEFORE、AFTER和INSTEAD OF。'),
        ('medium', 'single', '存储过程与函数的主要区别是？',
         json.dumps(['函数必须返回值', '存储过程必须返回值', '两者相同', '函数不能接受参数']),
         'A', '函数必须返回一个值，而存储过程可以不返回或返回多个值。'),
        ('medium', 'single', '以下哪个不是PL/SQL的组成部分？',
         json.dumps(['声明部分', '执行部分', '异常处理部分', '编译部分']),
         'D', 'PL/SQL包含声明、执行和异常处理三个部分。'),
        ('easy', 'multi', '以下关于存储过程的说法正确的有？',
         json.dumps(['可以接受参数', '可以返回值', '可以包含条件分支', '可以包含循环']),
         'ABCD', '存储过程可以包含参数、返回值、条件分支和循环。'),
        ('hard', 'single', '触发器的类型不包括？',
         json.dumps(['DML触发器', 'DDL触发器', '登录触发器', '查询触发器']),
         'D', '触发器类型有DML触发器、DDL触发器和登录触发器。'),
        ('medium', 'single', '事务的ACID特性中，C代表？',
         json.dumps(['一致性', '原子性', '隔离性', '持久性']),
         'A', 'ACID中C代表Consistency（一致性）。'),
    ],
    9: [  # 关系查询处理和查询优化
        ('easy', 'single', '查询处理的第一步是？',
         json.dumps(['解析和翻译', '优化', '执行', '存储']),
         'A', '查询处理步骤：解析翻译→优化→执行。'),
        ('medium', 'single', '查询优化的目标是？',
         json.dumps(['减少磁盘I/O和CPU时间', '增加执行时间', '减少数据量', '增加存储空间']),
         'A', '查询优化的目标是减少磁盘存取和CPU时间，提高查询效率。'),
        ('medium', 'single', '关系代数的等价变换规则不包括？',
         json.dumps(['选择与投影的交换律', '选择与笛卡尔积的交换律', '选择与并的分配律', '选择与差的分配律']),
         'D', '选择与差不满足分配律。'),
        ('medium', 'single', '以下哪种索引对范围查询最有效？',
         json.dumps(['B+树索引', '哈希索引', '位图索引', '全文索引']),
         'A', 'B+树索引对范围查询和排序最有效。'),
        ('easy', 'single', '访问路径的选择标准是？',
         json.dumps(['磁盘I/O次数', 'CPU使用率', '内存大小', '数据类型']),
         'A', '访问路径选择的主要标准是磁盘I/O次数。'),
        ('medium', 'single', '代价估算的主要因素是？',
         json.dumps(['磁盘I/O、CPU时间、内存访问', '数据量、网络速度', '用户数量、响应时间', '查询次数、缓存命中率']),
         'A', '代价估算主要考虑磁盘I/O、CPU时间和内存访问。'),
        ('hard', 'single', '下列关于查询优化的说法，正确的是？',
         json.dumps(['优化器总能找到最优方案', '启发式优化基于经验规则', '代价估算不需要统计信息', '所有查询都需要手动优化']),
         'B', '启发式优化基于经验规则，如先做选择再做连接。'),
    ],
    10: [  # 数据库恢复技术
        ('easy', 'single', '数据库故障的类型不包括？',
         json.dumps(['事务故障', '系统故障', '介质故障', '用户操作故障']),
         'D', '数据库故障分为事务故障、系统故障和介质故障。'),
        ('medium', 'single', '事务故障的恢复方法是？',
         json.dumps(['UNDO（回滚）', 'REDO（重做）', 'UNDO+REDO', '重新启动']),
         'A', '事务故障通过UNDO（回滚）来恢复。'),
        ('medium', 'single', '系统故障的恢复方法是？',
         json.dumps(['UNDO', 'REDO', 'UNDO+REDO', '删除重建']),
         'C', '系统故障恢复需要同时UNDO未完成事务和REDO已提交事务。'),
        ('medium', 'single', '介质故障的恢复方法是？',
         json.dumps(['UNDO', 'REDO', '从备份恢复+日志REDO', '重新启动']),
         'C', '介质故障需要从备份恢复，再利用日志REDO。'),
        ('easy', 'single', '日志文件的作用是？',
         json.dumps(['记录数据库的所有更新操作', '存储用户数据', '管理权限', '提高性能']),
         'A', '日志文件记录数据库的所有更新操作，用于故障恢复。'),
        ('medium', 'single', '以下关于日志技术的说法正确的是？',
         json.dumps(['先写日志协议', '先写数据库协议', '日志和数据库同时写', '不需要日志']),
         'A', '先写日志协议（Write-Ahead Logging）是恢复的基本原则。'),
        ('medium', 'single', '检查点技术的作用是？',
         json.dumps(['减少恢复时间', '增加存储空间', '提高查询速度', '增加事务数量']),
         'A', '检查点技术通过定期刷新脏页到磁盘来减少恢复时间。'),
        ('hard', 'single', '以下关于恢复的说法，错误的是？',
         json.dumps(['事务故障由DBMS自动恢复', '系统故障需要重启恢复', '介质故障需要备份恢复', '所有故障都可以自动恢复']),
         'D', '介质故障需要手动从备份恢复，不是所有故障都能自动恢复。'),
        ('medium', 'single', 'REDLOG的作用是？',
         json.dumps(['记录已提交事务的更新', '记录未提交事务', '记录所有事务', '记录检查点']),
         'A', 'REDO LOG记录已提交事务的更新，用于重做。'),
        ('medium', 'single', 'UNDOLOG的作用是？',
         json.dumps(['记录已提交事务', '记录事务的逆向操作', '记录所有查询', '记录备份']),
         'B', 'UNDO LOG记录事务的逆向操作，用于回滚。'),
    ],
    11: [  # 并发控制
        ('easy', 'single', '并发控制的主要方法是？',
         json.dumps(['封锁', '加密', '备份', '压缩']),
         'A', '封锁是并发控制的主要方法。'),
        ('medium', 'single', '封锁的基本类型不包括？',
         json.dumps(['共享锁(S锁)', '排他锁(X锁)', '意向锁', '读写锁']),
         'D', '基本封锁类型是S锁和X锁，意向锁是加强的封锁。'),
        ('medium', 'single', '三级封锁协议中，二级封锁协议可以防止？',
         json.dumps(['丢失修改', '读脏数据', '不可重复读', '幻读']),
         'A', '二级封锁协议可以防止丢失修改和读脏数据。'),
        ('medium', 'single', '活锁的解决方法是？',
         json.dumps(['先来先服务', '死锁检测', '死锁预防', '超时机制']),
         'A', '活锁通过先来先服务策略解决。'),
        ('medium', 'single', '死锁的四个必要条件不包括？',
         json.dumps(['互斥条件', '请求与保持条件', '不剥夺条件', '并发执行条件']),
         'D', '死锁的四个必要条件是互斥、请求与保持、不剥夺和循环等待。'),
        ('easy', 'single', '死锁预防的基本方法是？',
         json.dumps(['破坏死锁的必要条件', '等待并重试', '回滚所有事务', '使用单线程']),
         'A', '死锁预防通过破坏四个必要条件中的一个或多个来实现。'),
        ('medium', 'single', '以下哪种方法用于死锁检测？',
         json.dumps(['超时机制', '等待图法', '先来先服务', '时间戳排序']),
         'B', '等待图法是常用的死锁检测方法。'),
        ('medium', 'single', '可串行化调度的判定标准是？',
         json.dumps(['冲突可串行化', '结果可串行化', '执行顺序', '调度时间']),
         'A', '常用的可串行化判定标准是冲突可串行化。'),
        ('hard', 'single', '时间戳排序协议中，事务的时间戳是？',
         json.dumps(['事务开始的时间', '事务提交的时间', '系统分配的唯一标识', '用户指定的时间']),
         'C', '时间戳是系统为每个事务分配的唯一单调递增标识。'),
        ('medium', 'single', '以下关于封锁协议的说法，正确的是？',
         json.dumps(['一级封锁协议可以防止丢失修改', '二级封锁协议可以防止不可重复读', '三级封锁协议不能防止幻读', '封锁协议只能防止死锁']),
         'A', '一级封锁协议可以防止丢失修改，二级还能防止读脏数据。'),
    ],
}

# Map knowledge points by chapter and insert questions
inserted_count = 0
for chapter_id, templates in question_templates.items():
    kp_list = chapter_kps.get(chapter_id, [])
    if not kp_list:
        print(f"WARNING: No knowledge points for chapter {chapter_id}")
        continue
    
    # Distribute questions across knowledge points
    for i, template in enumerate(templates):
        kp_idx = i % len(kp_list)
        kp_id = kp_list[kp_idx][0]
        
        difficulty, qtype, stem, options, answer, analysis = template
        
        q = Question(
            knowledge_point_id=kp_id,
            type=qtype,
            difficulty=difficulty,
            stem=stem,
            options=options if qtype != 'judge' else None,
            answer=answer,
            analysis=analysis,
            order_index=i + 1
        )
        db.add(q)
        inserted_count += 1
    
    print(f"Chapter {chapter_id}: Inserted {len(templates)} questions across {len(kp_list)} knowledge points")

db.commit()
print(f"\nTotal inserted: {inserted_count} questions")

# Verify
total_questions = db.query(Question).count()
print(f"Total questions in database: {total_questions}")

# Questions per type
from sqlalchemy import func
type_counts = db.query(Question.type, func.count(Question.id)).group_by(Question.type).all()
for qtype, count in type_counts:
    print(f"  {qtype}: {count}")
