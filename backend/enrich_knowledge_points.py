"""
知识点内容扩充脚本
为所有知识点补充：原理说明、分步操作指引、实操注意事项、常见问题、专属配图
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import KnowledgePoint

db = SessionLocal()

# 图片基础URL（使用 pollinations.ai 免费图片生成服务）
IMG_BASE = "https://image.pollinations.ai/prompt/{prompt}?width=1024&height=576&nologo=true&seed={seed}"

ENRICHMENT = {
    "数据库的定义与特征": {
        "detail_content": "数据库（Database）是长期存储在计算机内、有组织的、可共享的大量数据的集合。它具有以下核心特征：数据结构化（按特定数据模型组织）、数据共享性高（多用户多应用同时访问）、数据冗余度低（避免重复存储）、数据独立性高（物理结构与逻辑结构分离）、数据由DBMS统一管理和控制。",
        "key_points": ["长期存储在计算机内", "有组织的数据集合", "可被多用户共享", "由DBMS统一管理", "数据冗余度低、独立性高"],
        "learning_steps": [
            "理解数据、数据库、数据库系统、数据库管理系统四个概念的区别与联系",
            "掌握数据库的四大核心特征：结构化、共享性、低冗余、独立性",
            "结合实际应用场景（如教务系统、电商系统）理解数据库的作用",
            "能够区分文件系统与数据库系统的本质差异"
        ],
        "tips": [
            "不要混淆'数据库'和'数据库管理系统'，前者是数据集合，后者是管理软件",
            "数据独立性分为物理独立性和逻辑独立性，是数据库的重要优势",
            "共享性高不等于没有冗余，适度冗余有时是必要的"
        ],
        "faq": [
            {"question": "文件系统和数据库系统有什么区别？", "answer": "文件系统数据共享性差、冗余度大、独立性差；数据库系统数据结构化、共享性高、冗余度低、独立性高，由DBMS统一管理。"},
            {"question": "数据独立性是什么意思？", "answer": "数据独立性是指应用程序与数据库的数据结构之间相互独立。包括物理独立性（存储结构变化不影响逻辑结构）和逻辑独立性（逻辑结构变化不影响应用程序）。"}
        ],
        "image_url": IMG_BASE.format(prompt="database system architecture diagram with connected data blocks, clean educational illustration, blue and white color scheme", seed=1)
    },
    "数据库系统的三级模式结构": {
        "detail_content": "数据库系统的三级模式结构由外模式、模式、内模式组成。模式（逻辑模式）是数据库中全体数据的逻辑结构和特征的描述，是所有用户的公共数据视图。外模式（用户模式）是数据库用户能够看见和使用的局部数据的逻辑结构和特征的描述。内模式（存储模式）是数据物理结构和存储方式的描述。两级映像保证了数据的独立性：外模式/模式映像保证逻辑独立性，模式/内模式映像保证物理独立性。",
        "key_points": ["三级模式：外模式、模式、内模式", "两级映像保证数据独立性", "外模式/模式映像→逻辑独立性", "模式/内模式映像→物理独立性"],
        "learning_steps": [
            "理解三级模式的含义：外模式（用户视图）、模式（全局逻辑结构）、内模式（物理存储）",
            "理解两级映像的作用：如何通过映像实现数据与程序的独立",
            "掌握逻辑独立性和物理独立性的实现原理",
            "能够画出三级模式结构的示意图"
        ],
        "tips": [
            "一个数据库只有一个模式和一个内模式，但可以有多个外模式",
            "外模式是模式的子集，每个用户看到的是自己的外模式",
            "三级模式是数据库系统体系结构的核心"
        ],
        "faq": [
            {"question": "为什么需要三级模式结构？", "answer": "三级模式结构实现了数据的独立性，使应用程序不随数据物理结构或逻辑结构的变化而改变，降低了应用程序的维护成本。"},
            {"question": "外模式和模式有什么区别？", "answer": "模式是全局数据的逻辑结构描述，是所有用户共享的；外模式是局部数据的逻辑结构描述，是特定用户的数据视图，通常是模式的子集。"}
        ],
        "image_url": IMG_BASE.format(prompt="three schema architecture diagram of database system, external schema conceptual schema internal schema, two level mappings, educational infographic", seed=2)
    },
    "数据库管理系统的功能与组成": {
        "detail_content": "数据库管理系统（DBMS）是位于用户与操作系统之间的一层数据管理软件，主要功能包括：数据定义（DDL）、数据操纵（DML）、数据库运行管理、数据库建立与维护、数据通信。DBMS通常由以下几部分组成：数据定义语言及其翻译处理程序、数据操纵语言及其编译程序、数据库运行控制程序、实用程序。",
        "key_points": ["数据定义功能（DDL）", "数据操纵功能（DML）", "数据库运行管理", "数据库建立与维护", "数据通信功能"],
        "learning_steps": [
            "理解DBMS在系统层次结构中的位置（用户-应用-DBMS-OS-硬件）",
            "掌握DBMS的五大核心功能及其含义",
            "了解DBMS的主要组成部分",
            "能够举例说明DBMS如何完成数据管理任务"
        ],
        "tips": [
            "DDL用于定义数据库结构，DML用于操作数据，不要混淆",
            "DBMS不是数据库，是管理数据库的软件",
            "常见DBMS有MySQL、Oracle、SQL Server、PostgreSQL等"
        ],
        "faq": [
            {"question": "DDL和DML有什么区别？", "answer": "DDL（数据定义语言）用于定义数据库结构，如CREATE、ALTER、DROP；DML（数据操纵语言）用于操作数据，如SELECT、INSERT、UPDATE、DELETE。"},
            {"question": "DBMS必须提供哪些功能？", "answer": "DBMS必须提供数据定义、数据操纵、数据库运行管理、数据库建立与维护、数据通信这五大基本功能。"}
        ],
        "image_url": IMG_BASE.format(prompt="DBMS database management system architecture components diagram, data definition manipulation control, clean technical illustration", seed=3)
    },
    "数据模型的三要素": {
        "detail_content": "数据模型是数据库结构的基础，用于描述数据的组织方式。数据模型包含三个要素：数据结构（描述数据库的组成对象及对象之间的联系）、数据操作（对数据库中各种对象的实例允许执行的操作的集合）、数据的完整性约束条件（一组完整性规则的集合，用以限定符合数据模型的数据库状态以及状态的变化）。",
        "key_points": ["数据结构：描述数据及联系", "数据操作：增删改查等操作", "完整性约束：保证数据正确性"],
        "learning_steps": [
            "理解数据模型的定义和作用",
            "掌握数据模型三要素的具体含义",
            "能够举例说明不同数据模型（层次、网状、关系）的三要素",
            "理解完整性约束的重要性"
        ],
        "tips": [
            "数据结构是数据模型中最基本的部分",
            "数据操作包括检索和更新两大类",
            "完整性约束保证数据的正确性和相容性"
        ],
        "faq": [
            {"question": "数据模型的三要素是什么？", "answer": "数据结构、数据操作、数据的完整性约束条件。"},
            {"question": "为什么需要数据完整性约束？", "answer": "完整性约束保证数据的正确性、有效性和相容性，防止无效数据进入数据库。"}
        ],
        "image_url": IMG_BASE.format(prompt="data model three elements diagram, data structure data operations integrity constraints, educational infographic with icons", seed=4)
    },
    "常见数据模型介绍（层次、网络、关系、面向对象）": {
        "detail_content": "常见数据模型包括：层次模型（用树型结构表示实体及联系，有且仅有一个根节点，其他节点有且仅有一个父节点）、网状模型（用网状结构表示，允许一个节点有多个父节点）、关系模型（用二维表表示实体及联系，是当前主流模型）、面向对象模型（将面向对象概念引入数据库，支持复杂对象、继承、封装等）。",
        "key_points": ["层次模型：树型结构", "网状模型：网状结构", "关系模型：二维表（主流）", "面向对象模型：支持复杂对象"],
        "learning_steps": [
            "理解四种数据模型的基本结构",
            "掌握每种模型的优缺点和适用场景",
            "理解关系模型成为主流的原因",
            "能够用图示表示不同数据模型"
        ],
        "tips": [
            "层次模型中除根节点外，每个节点有且仅有一个父节点",
            "网状模型允许多个父节点，更灵活但更复杂",
            "关系模型用二维表表示，简单直观，是当前主流"
        ],
        "faq": [
            {"question": "关系模型为什么成为主流？", "answer": "关系模型以二维表为基础，结构简单直观，有严格的数学基础（关系代数），数据独立性高，易于理解和使用。"},
            {"question": "层次模型和网状模型的主要区别是什么？", "answer": "层次模型是树型结构，每个节点只有一个父节点；网状模型是网状结构，节点可以有多个父节点。"}
        ],
        "image_url": IMG_BASE.format(prompt="comparison of four data models hierarchical network relational object oriented, diagram with tree graph table object structures", seed=5)
    },
    "关系模型的基本概念（关系、元组、属性、码）": {
        "detail_content": "关系模型由关系数据结构、关系操作集合、关系完整性约束三部分组成。在关系模型中：关系（Relation）即二维表，一个关系对应一张表；元组（Tuple）即表中的一行；属性（Attribute）即表中的一列；码（Key）是能唯一标识元组的属性或属性组，包括候选码、主码、外码等。",
        "key_points": ["关系=二维表", "元组=表的一行", "属性=表的一列", "码=唯一标识元组的属性"],
        "learning_steps": [
            "理解关系、元组、属性、域、码等基本概念",
            "掌握主码、候选码、外码的区别",
            "理解关系的性质（列同质、列无序、行无序、不允许重复元组等）",
            "能够从实际表格中识别关系的各个组成部分"
        ],
        "tips": [
            "关系中的列是同质的，即同一列的数据类型相同",
            "关系中不允许出现完全相同的元组",
            "主码不能取空值（实体完整性规则）"
        ],
        "faq": [
            {"question": "候选码和主码有什么区别？", "answer": "候选码是能唯一标识元组的属性或属性组，主码是从候选码中选定的一个作为主码。一个关系可以有多个候选码，但只能有一个主码。"},
            {"question": "什么是外码？", "answer": "外码是关系R中的一个属性或属性组，它不是R的主码，但它是另一个关系S的主码，用于建立两个关系之间的联系。"}
        ],
        "image_url": IMG_BASE.format(prompt="relational model concepts illustration, table with rows tuple columns attribute keys, educational diagram showing relation structure", seed=6)
    },
    "关系的完整性约束（实体完整性、参照完整性、用户定义完整性）": {
        "detail_content": "关系模型有三类完整性约束：实体完整性（主码不能为空值，确保元组可唯一标识）、参照完整性（外码的值必须等于被参照关系中某个主码的值，或者为空值，确保引用的有效性）、用户定义完整性（用户针对具体数据定义的约束条件，如性别只能是男或女、年龄必须在0-150之间等）。",
        "key_points": ["实体完整性：主码非空", "参照完整性：外码引用有效", "用户定义完整性：自定义业务规则"],
        "learning_steps": [
            "理解三类完整性约束的定义和作用",
            "掌握实体完整性和参照完整性的具体规则",
            "能够设计用户定义完整性约束",
            "理解违反完整性约束时的处理策略"
        ],
        "tips": [
            "实体完整性和参照完整性是关系模型必须满足的约束",
            "参照完整性中，外码可以为空值（除非它是本关系主码的一部分）",
            "用户定义完整性根据具体业务需求设定"
        ],
        "faq": [
            {"question": "违反参照完整性时如何处理？", "answer": "通常有三种处理策略：拒绝执行（默认）、级联操作（同步更新/删除）、设置为空值。"},
            {"question": "为什么需要用户定义完整性？", "answer": "因为实体完整性和参照完整性是通用规则，无法覆盖具体业务需求，如成绩必须在0-100之间，这就需要用户定义完整性来约束。"}
        ],
        "image_url": IMG_BASE.format(prompt="database integrity constraints diagram, entity integrity referential integrity user defined integrity, with examples and rules", seed=7)
    },
    "关系代数的基本运算（选择、投影、并、差、笛卡尔积）": {
        "detail_content": "关系代数的基本运算包括五种：选择（σ，从关系中选取满足条件的元组）、投影（π，从关系中选取若干属性列）、并（∪，两个关系的所有元组合并，去重）、差（-，属于一个关系但不属于另一个关系的元组）、笛卡尔积（×，两个关系元组的所有组合）。这些是关系代数的基础操作。",
        "key_points": ["选择σ：按条件选行", "投影π：选列", "并∪：合并去重", "差-：A中不属于B的", "笛卡尔积×：所有组合"],
        "learning_steps": [
            "理解五种基本运算的定义和符号",
            "掌握每种运算的操作对象和结果",
            "能够用关系代数表达式表示查询需求",
            "通过实例练习加深理解"
        ],
        "tips": [
            "选择是行运算，投影是列运算",
            "并运算要求两个关系的属性个数和对应属性域相同",
            "笛卡尔积会产生大量元组，实际查询中很少直接使用"
        ],
        "faq": [
            {"question": "选择和投影有什么区别？", "answer": "选择是从关系中选取满足条件的元组（行），投影是从关系中选取若干属性列（列）。选择不减少列数，投影不减少行数（去重除外）。"},
            {"question": "并运算的前提条件是什么？", "answer": "并运算要求两个关系是相容的，即属性个数相同，且对应属性的域相同。"}
        ],
        "image_url": IMG_BASE.format(prompt="relational algebra basic operations diagram, selection projection union difference cartesian product with examples", seed=8)
    },
    "关系代数的扩展运算（连接、自然连接、除）": {
        "detail_content": "关系代数的扩展运算建立在基本运算之上：连接（⋈，从两个关系的笛卡尔积中选取满足连接条件的元组）、自然连接（特殊的等值连接，要求连接属性名相同，结果中去掉重复列）、除（÷，用于包含查询，R÷S的结果是R中满足S所有元组的属性值）。",
        "key_points": ["连接：按条件组合两关系", "自然连接：等值连接+去重列", "除：包含查询"],
        "learning_steps": [
            "理解连接运算的定义和分类（θ连接、等值连接、自然连接）",
            "掌握自然连接的特点（自动匹配同名列，去重）",
            "理解除运算的含义和应用场景",
            "能够用连接和除运算表达复杂查询"
        ],
        "tips": [
            "自然连接是最常用的连接方式",
            "除运算用于'包含所有'类型的查询，如'选修了所有课程的学生'",
            "连接运算可以用基本运算（笛卡尔积+选择）表示"
        ],
        "faq": [
            {"question": "等值连接和自然连接有什么区别？", "answer": "等值连接是按相等条件连接，保留重复列；自然连接是特殊的等值连接，要求连接属性名相同，结果中去掉重复列。"},
            {"question": "除运算适用于什么场景？", "answer": "除运算适用于'包含所有'类型的查询，如'查询选修了所有课程的学生'。"}
        ],
        "image_url": IMG_BASE.format(prompt="relational algebra extended operations diagram, join natural join division with examples and visual representation", seed=9)
    },
    "关系代数表达式的优化": {
        "detail_content": "关系代数表达式优化的目的是提高查询效率。优化策略包括：选择运算应尽可能先做（减少元组数）、投影运算和选择运算同时进行（减少扫描次数）、将投影与其前后的双目运算结合、选择与其前面要执行的笛卡尔积结合起来成为一个连接运算、找出公共子表达式。",
        "key_points": ["选择尽可能先做", "投影选择合并执行", "笛卡尔积+选择→连接", "提取公共子表达式"],
        "learning_steps": [
            "理解查询优化的必要性和目标",
            "掌握五种基本优化策略",
            "能够对给定的关系代数表达式进行优化",
            "理解查询优化的代价估算"
        ],
        "tips": [
            "选择先做是最重要的优化策略，能大幅减少后续运算的数据量",
            "优化的目标是减少I/O次数和CPU开销",
            "DBMS的查询优化器会自动进行优化"
        ],
        "faq": [
            {"question": "为什么要进行查询优化？", "answer": "不同的关系代数表达式可以表示相同的查询，但执行效率可能相差很大。优化可以显著减少I/O操作和计算量，提高查询效率。"},
            {"question": "选择运算为什么要先做？", "answer": "选择运算可以过滤掉不需要的元组，减少后续运算（如连接、笛卡尔积）的数据量，从而大幅提高执行效率。"}
        ],
        "image_url": IMG_BASE.format(prompt="relational algebra query optimization flowchart, before and after optimization tree comparison, database performance illustration", seed=10)
    },
    "SQL的数据定义语言（DDL）": {
        "detail_content": "SQL的数据定义语言（DDL）用于定义和管理数据库的结构，主要包括：CREATE（创建数据库、表、视图、索引等）、ALTER（修改已有对象的结构）、DROP（删除数据库对象）。CREATE TABLE用于创建表，定义列名、数据类型、约束条件（主码、外码、非空、唯一等）。",
        "key_points": ["CREATE：创建对象", "ALTER：修改结构", "DROP：删除对象", "支持定义各种约束"],
        "learning_steps": [
            "掌握CREATE DATABASE、CREATE TABLE语句的语法",
            "掌握常见数据类型（INT、VARCHAR、DATE、DECIMAL等）",
            "掌握约束定义（PRIMARY KEY、FOREIGN KEY、NOT NULL、UNIQUE、CHECK、DEFAULT）",
            "掌握ALTER TABLE（ADD、MODIFY、DROP COLUMN）和DROP TABLE语句"
        ],
        "tips": [
            "定义表时注意数据类型的选择，避免溢出或浪费空间",
            "主码默认非空且唯一",
            "外码引用的必须是被参照表的主码或候选码"
        ],
        "faq": [
            {"question": "PRIMARY KEY和UNIQUE有什么区别？", "answer": "PRIMARY KEY不允许空值，一个表只能有一个；UNIQUE允许空值（多个NULL），一个表可以有多个UNIQUE约束。"},
            {"question": "DROP和DELETE有什么区别？", "answer": "DROP删除整个表结构和数据，DELETE只删除表中的数据（保留表结构）。"}
        ],
        "image_url": IMG_BASE.format(prompt="SQL DDL data definition language syntax examples, create alter drop table statements, code illustration", seed=11)
    },
    "SQL的数据操纵语言（DML）- 查询": {
        "detail_content": "SQL查询使用SELECT语句，基本语法为：SELECT [列名] FROM [表名] WHERE [条件] GROUP BY [列] HAVING [条件] ORDER BY [列] [ASC|DESC] LIMIT [数量]。查询是SQL最核心的功能，支持多表连接、子查询、集合运算等高级功能。",
        "key_points": ["SELECT指定列", "FROM指定表", "WHERE筛选行", "GROUP BY分组", "HAVING筛选组", "ORDER BY排序"],
        "learning_steps": [
            "掌握SELECT语句的基本语法和执行顺序",
            "掌握WHERE条件查询（比较、LIKE、IN、BETWEEN、IS NULL等）",
            "掌握多表连接查询（INNER JOIN、LEFT JOIN、RIGHT JOIN）",
            "掌握ORDER BY排序和LIMIT限制结果集"
        ],
        "tips": [
            "SELECT的执行顺序：FROM→WHERE→GROUP BY→HAVING→SELECT→ORDER BY",
            "避免使用SELECT *，明确列出需要的列",
            "WHERE在分组前筛选，HAVING在分组后筛选"
        ],
        "faq": [
            {"question": "WHERE和HAVING有什么区别？", "answer": "WHERE在分组前对行进行筛选，不能用聚集函数；HAVING在分组后对组进行筛选，可以用聚集函数。"},
            {"question": "LIKE中%和_有什么区别？", "answer": "%匹配任意多个字符（包括0个），_匹配恰好一个字符。"}
        ],
        "image_url": IMG_BASE.format(prompt="SQL SELECT query syntax breakdown, select from where group by having order by, educational diagram", seed=12)
    },
    "SQL的数据操纵语言（DML）- 插入、更新、删除": {
        "detail_content": "SQL的数据更新操作包括：INSERT INTO（插入数据）、UPDATE（更新数据）、DELETE（删除数据）。INSERT语句可以插入一行或多行数据；UPDATE语句用于修改已有数据，需配合WHERE条件限定范围；DELETE语句用于删除数据，同样需配合WHERE条件。",
        "key_points": ["INSERT：插入数据", "UPDATE：修改数据（配合WHERE）", "DELETE：删除数据（配合WHERE）"],
        "learning_steps": [
            "掌握INSERT INTO ... VALUES语法",
            "掌握INSERT INTO ... SELECT语法（从其他表复制数据）",
            "掌握UPDATE ... SET ... WHERE语法",
            "掌握DELETE FROM ... WHERE语法"
        ],
        "tips": [
            "UPDATE和DELETE语句一定要加WHERE条件，否则会修改/删除所有数据",
            "INSERT语句中列名和值要一一对应",
            "执行更新操作前建议先SELECT确认影响的行数"
        ],
        "faq": [
            {"question": "DELETE和TRUNCATE有什么区别？", "answer": "DELETE是DML语句，可以加WHERE条件，删除的记录可以回滚；TRUNCATE是DDL语句，清空整个表，速度更快但不能回滚。"},
            {"question": "如何一次插入多行数据？", "answer": "使用INSERT INTO table_name (col1, col2) VALUES (val1, val2), (val3, val4), ... 语法。"}
        ],
        "image_url": IMG_BASE.format(prompt="SQL DML insert update delete operations, syntax examples with table data modification illustration", seed=13)
    },
    "SQL的聚集函数与分组查询": {
        "detail_content": "SQL提供了聚集函数用于统计计算：COUNT（计数）、SUM（求和）、AVG（平均值）、MAX（最大值）、MIN（最小值）。GROUP BY子句用于将数据按某列分组，聚集函数会对每个分组分别计算。HAVING子句用于对分组结果进行筛选。",
        "key_points": ["COUNT/SUM/AVG/MAX/MIN", "GROUP BY分组", "HAVING筛选分组", "聚集函数忽略NULL值"],
        "learning_steps": [
            "掌握五个聚集函数的用法",
            "理解GROUP BY的分组原理",
            "掌握HAVING子句的用法（与WHERE的区别）",
            "能够编写复杂的分组统计查询"
        ],
        "tips": [
            "聚集函数自动忽略NULL值，COUNT(*)不忽略",
            "GROUP BY后面的列必须出现在SELECT中（除聚集函数外）",
            "HAVING中可以使用聚集函数，WHERE中不可以"
        ],
        "faq": [
            {"question": "COUNT(*)和COUNT(列名)有什么区别？", "answer": "COUNT(*)统计所有行数（包括NULL），COUNT(列名)统计该列非NULL的行数。"},
            {"question": "WHERE中能否使用聚集函数？", "answer": "不能。聚集函数只能用于SELECT列表、HAVING子句和ORDER BY子句中。"}
        ],
        "image_url": IMG_BASE.format(prompt="SQL aggregate functions and group by diagram, count sum avg max min with grouping and having examples", seed=14)
    },
    "SQL的嵌套查询与集合运算": {
        "detail_content": "嵌套查询（子查询）是指在一个查询的WHERE或HAVING子句中嵌入另一个SELECT查询。子查询可以分为相关子查询和不相关子查询。集合运算包括UNION（并）、INTERSECT（交）、EXCEPT（差），用于合并多个查询的结果。",
        "key_points": ["子查询：查询中嵌套查询", "IN/ANY/ALL量词", "UNION/INTERSECT/EXCEPT", "相关子查询与不相关子查询"],
        "learning_steps": [
            "理解子查询的概念和分类（相关/不相关）",
            "掌握IN、EXISTS、ANY、ALL等谓词的用法",
            "掌握UNION、INTERSECT、EXCEPT集合运算",
            "能够用子查询或连接表达复杂查询"
        ],
        "tips": [
            "子查询的结果可以作为外层查询的条件",
            "UNION会自动去重，UNION ALL不去重",
            "很多子查询可以用连接查询替代，连接通常效率更高"
        ],
        "faq": [
            {"question": "相关子查询和不相关子查询有什么区别？", "answer": "不相关子查询的执行不依赖外层查询，可以独立执行；相关子查询的执行依赖外层查询的值，需要反复执行。"},
            {"question": "UNION和JOIN有什么区别？", "answer": "UNION合并两个查询的行（纵向合并），要求列数和类型相同；JOIN合并两个表的列（横向合并）。"}
        ],
        "image_url": IMG_BASE.format(prompt="SQL nested queries and set operations diagram, subquery in where clause union intersect except examples", seed=15)
    },
    "SQL的视图定义与使用": {
        "detail_content": "视图（View）是从一个或几个基本表（或视图）导出的虚表，只存放视图的定义，不存放视图对应的数据。视图可以使用CREATE VIEW语句创建，使用DROP VIEW语句删除。通过视图可以简化查询、提供数据安全性、提供逻辑数据独立性。",
        "key_points": ["视图是虚表，只存定义", "CREATE VIEW创建", "DROP VIEW删除", "简化查询、提高安全性"],
        "learning_steps": [
            "理解视图的概念和作用",
            "掌握CREATE VIEW和DROP VIEW语句",
            "掌握视图的查询和更新（可更新视图的条件）",
            "理解视图的优点和限制"
        ],
        "tips": [
            "视图中不存储数据，数据来自基本表",
            "对视图的查询会转换为对基本表的查询",
            "不是所有视图都可以更新（如含聚集函数、GROUP BY的视图不可更新）"
        ],
        "faq": [
            {"question": "视图和基本表有什么区别？", "answer": "基本表是实际存储数据的表，视图是虚表，只存储定义不存储数据。对视图的操作最终转换为对基本表的操作。"},
            {"question": "为什么要使用视图？", "answer": "视图可以简化复杂查询、提供数据安全性（隐藏敏感数据）、提供逻辑数据独立性、方便数据共享。"}
        ],
        "image_url": IMG_BASE.format(prompt="SQL view concept diagram, virtual table derived from base tables, create view syntax and usage illustration", seed=16)
    },
    "SQL的存储过程与触发器": {
        "detail_content": "存储过程（Stored Procedure）是一组预先编译好的SQL语句的集合，存储在数据库中，可以反复调用。触发器（Trigger）是一种特殊的存储过程，当对表执行INSERT、UPDATE、DELETE操作时自动触发执行。存储过程可以提高执行效率、封装业务逻辑；触发器可以实现复杂的数据完整性约束。",
        "key_points": ["存储过程：预编译SQL集合", "CREATE PROCEDURE创建", "触发器：自动触发执行", "CREATE TRIGGER创建"],
        "learning_steps": [
            "理解存储过程的概念和优点",
            "掌握CREATE PROCEDURE和CALL语句",
            "理解触发器的概念和触发时机（BEFORE/AFTER）",
            "掌握CREATE TRIGGER语句"
        ],
        "tips": [
            "存储过程可以接受参数并返回结果",
            "触发器可以用于审计日志、数据验证、级联更新等",
            "过多的触发器会影响性能，应谨慎使用"
        ],
        "faq": [
            {"question": "存储过程和函数有什么区别？", "answer": "存储过程可以有多个返回值（通过OUT参数），函数只能返回一个值；存储过程可以独立调用，函数通常在SQL语句中调用。"},
            {"question": "触发器的触发时机有哪些？", "answer": "触发器可以在BEFORE（操作前）或AFTER（操作后）触发，针对INSERT、UPDATE、DELETE三种操作。"}
        ],
        "image_url": IMG_BASE.format(prompt="SQL stored procedures and triggers diagram, procedure creation trigger execution flow, database automation illustration", seed=17)
    },
    "函数依赖的基本概念": {
        "detail_content": "函数依赖是关系数据库设计理论的基础。设R(U)是属性集U上的关系模式，X、Y是U的子集。若对于R(U)的任意一个可能的关系r，r中不可能存在两个元组在X上的属性值相等，而在Y上的属性值不等，则称X函数确定Y或Y函数依赖于X，记作X→Y。",
        "key_points": ["X→Y表示X函数确定Y", "完全函数依赖与部分函数依赖", "传递函数依赖", "是规范化理论的基础"],
        "learning_steps": [
            "理解函数依赖的定义",
            "掌握完全函数依赖、部分函数依赖、传递函数依赖",
            "理解码的函数依赖定义（候选码、主码、外码、全码）",
            "能够从实际数据中识别函数依赖"
        ],
        "tips": [
            "函数依赖是语义层面的概念，需要根据业务规则判断",
            "部分函数依赖是指X→Y，但Y不完全依赖于X的所有属性",
            "传递函数依赖是指X→Y，Y→Z，且Y不函数确定X"
        ],
        "faq": [
            {"question": "什么是部分函数依赖？", "answer": "部分函数依赖是指在关系模式R(U)中，如果X→Y，且存在X的真子集X'使得X'→Y，则称Y对X部分函数依赖。"},
            {"question": "函数依赖和多值依赖有什么区别？", "answer": "函数依赖X→Y表示X的值唯一确定Y的值；多值依赖X→→Y表示X的值确定Y的一组值（多值），与其他属性无关。"}
        ],
        "image_url": IMG_BASE.format(prompt="functional dependency concept diagram, X determines Y arrow, complete partial transitive dependency types", seed=18)
    },
    "第一范式（1NF）、第二范式（2NF）": {
        "detail_content": "第一范式（1NF）：关系模式R的所有属性都是不可再分的基本数据项。第二范式（2NF）：在满足1NF的基础上，消除非主属性对码的部分函数依赖，即每个非主属性都完全函数依赖于码。1NF是关系模式的基本要求，2NF进一步消除冗余。",
        "key_points": ["1NF：属性不可再分", "2NF：消除部分函数依赖", "2NF在1NF基础上"],
        "learning_steps": [
            "理解1NF的要求（属性原子性）",
            "理解2NF的要求（消除部分函数依赖）",
            "掌握1NF到2NF的规范化方法（模式分解）",
            "能够判断关系模式属于第几范式"
        ],
        "tips": [
            "1NF要求每列都是原子值，不能是集合或复合值",
            "2NF主要针对有复合码的关系，消除非主属性对码的部分依赖",
            "不符合2NF会导致数据冗余和更新异常"
        ],
        "faq": [
            {"question": "为什么需要满足2NF？", "answer": "不满足2NF会导致数据冗余（同一数据重复存储）、插入异常、删除异常、更新异常等问题。"},
            {"question": "如何将关系模式从1NF规范化到2NF？", "answer": "通过模式分解，将部分函数依赖分离出来，使每个非主属性都完全函数依赖于码。"}
        ],
        "image_url": IMG_BASE.format(prompt="database normalization 1NF 2NF diagram, first normal form attribute atomicity, second normal form partial dependency elimination", seed=19)
    },
    "第三范式（3NF）、BC范式（BCNF）": {
        "detail_content": "第三范式（3NF）：在满足2NF的基础上，消除非主属性对码的传递函数依赖。BC范式（BCNF）：在满足3NF的基础上，消除主属性对码的部分和传递函数依赖。BCNF是比3NF更严格的范式，要求每个决定因素都包含码。",
        "key_points": ["3NF：消除传递函数依赖", "BCNF：每个决定因素都含码", "BCNF比3NF更严格"],
        "learning_steps": [
            "理解3NF的要求（消除非主属性的传递依赖）",
            "理解BCNF的要求（消除主属性的部分/传递依赖）",
            "掌握3NF和BCNF的判断方法",
            "能够进行3NF和BCNF的规范化"
        ],
        "tips": [
            "3NF消除的是非主属性对码的传递依赖",
            "BCNF要求所有非平凡函数依赖X→Y，X都必须是超码",
            "大部分3NF关系也是BCNF"
        ],
        "faq": [
            {"question": "3NF和BCNF有什么区别？", "answer": "3NF允许主属性对码的部分和传递依赖，BCNF不允许。BCNF是比3NF更严格的范式。"},
            {"question": "是否一定要达到BCNF？", "answer": "不一定。BCNF可能会破坏函数依赖的保持性，有时为了保持函数依赖，可以接受3NF。实际应用中通常达到3NF即可。"}
        ],
        "image_url": IMG_BASE.format(prompt="database normalization 3NF BCNF diagram, third normal form transitive dependency, Boyce-Codd normal form comparison", seed=20)
    },
    "第四范式（4NF）、第五范式（5NF）": {
        "detail_content": "第四范式（4NF）：在满足BCNF的基础上，消除非平凡且非函数依赖的多值依赖。第五范式（5NF）：在满足4NF的基础上，消除连接依赖。4NF和5NF是更高层次的范式，处理更复杂的数据依赖问题。",
        "key_points": ["4NF：消除多值依赖", "5NF：消除连接依赖", "比BCNF更高级"],
        "learning_steps": [
            "理解多值依赖的概念",
            "掌握4NF的定义和判断方法",
            "理解连接依赖的概念",
            "了解5NF的定义"
        ],
        "tips": [
            "多值依赖是属性之间的一种约束关系",
            "4NF要求关系中只存在函数依赖，不存在非函数依赖的多值依赖",
            "5NF在实际应用中较少使用"
        ],
        "faq": [
            {"question": "多值依赖和函数依赖有什么区别？", "answer": "函数依赖X→Y表示X唯一确定Y；多值依赖X→→Y表示X确定Y的一组值。函数依赖是多值依赖的特殊情况。"},
            {"question": "实际开发中需要达到第几范式？", "answer": "通常达到3NF或BCNF即可，4NF和5NF在实际应用中较少使用，因为可能影响查询效率。"}
        ],
        "image_url": IMG_BASE.format(prompt="database normalization 4NF 5NF diagram, fourth normal form multivalued dependency, fifth normal form join dependency", seed=21)
    },
    "模式分解的无损连接性和保持函数依赖性": {
        "detail_content": "模式分解是将一个关系模式分解为多个子关系模式，以达到更高的范式。好的分解需要满足两个条件：无损连接性（分解后的关系通过自然连接可以还原为原来的关系，不丢失信息）和保持函数依赖性（原关系中的所有函数依赖在分解后的关系中都能得到保持）。",
        "key_points": ["无损连接性：不丢失信息", "保持函数依赖：依赖不丢失", "两者是分解的目标"],
        "learning_steps": [
            "理解模式分解的含义",
            "掌握无损连接性的判断方法（chase检验法）",
            "掌握保持函数依赖性的判断方法",
            "理解两者的权衡关系"
        ],
        "tips": [
            "无损连接性保证数据不丢失，是必须满足的",
            "保持函数依赖性保证语义不丢失，但有时需要在无损连接和保持依赖之间权衡",
            "无损连接分解不一定保持函数依赖，反之亦然"
        ],
        "faq": [
            {"question": "无损连接性和保持函数依赖性能否同时满足？", "answer": "不一定能同时满足。有时为了保持函数依赖，需要牺牲无损连接性；反之亦然。实际应用中需要权衡。"},
            {"question": "如何判断分解是否是无损连接的？", "answer": "可以使用chase检验法（追踪法），构造一个表格，根据函数依赖进行变换，如果某一行变成全a，则是无损连接分解。"}
        ],
        "image_url": IMG_BASE.format(prompt="schema decomposition lossless join and dependency preservation diagram, database normalization concepts", seed=22)
    },
    "数据库设计的全过程": {
        "detail_content": "数据库设计分为六个阶段：需求分析（了解用户需求）、概念结构设计（设计E-R图）、逻辑结构设计（E-R图转换为关系模式）、物理结构设计（选择存储结构和存取方法）、数据库实施（建库、建表、加载数据）、数据库运行和维护（监控、优化、备份）。",
        "key_points": ["需求分析→概念设计→逻辑设计→物理设计→实施→运行维护", "E-R图是概念设计的核心", "范式用于逻辑设计优化"],
        "learning_steps": [
            "掌握数据库设计的六个阶段",
            "掌握需求分析的方法和产出（数据字典、数据流图）",
            "掌握概念设计（E-R图设计）",
            "掌握逻辑设计（E-R图转关系模式）和物理设计"
        ],
        "tips": [
            "需求分析是数据库设计的基础，决定后续设计的质量",
            "E-R图用矩形表示实体、椭圆表示属性、菱形表示联系",
            "逻辑设计中要将E-R图转换为关系模式，并进行规范化"
        ],
        "faq": [
            {"question": "数据库设计的核心阶段是什么？", "answer": "概念结构设计和逻辑结构设计是核心阶段。概念设计确定数据模型（E-R图），逻辑设计将其转换为具体的关系模式。"},
            {"question": "E-R图如何转换为关系模式？", "answer": "实体转换为关系，属性转换为列，联系根据基数（1:1、1:n、m:n）转换为关系或外键。"}
        ],
        "image_url": IMG_BASE.format(prompt="database design process six stages flowchart, requirements analysis conceptual logical physical implementation maintenance", seed=23)
    },
    "事务的ACID特性": {
        "detail_content": "事务（Transaction）是用户定义的一个数据库操作序列，这些操作要么全做，要么全不做，是一个不可分割的工作单位。事务具有四个特性（ACID）：原子性（Atomicity，操作要么全做要么全不做）、一致性（Consistency，事务执行前后数据保持一致状态）、隔离性（Isolation，并发事务互不干扰）、持久性（Durability，事务提交后修改永久保存）。",
        "key_points": ["原子性A：全做或全不做", "一致性C：数据状态一致", "隔离性I：并发不干扰", "持久性D：修改永久保存"],
        "learning_steps": [
            "理解事务的定义和BEGIN...COMMIT/ROLLBACK语法",
            "掌握ACID四个特性的含义",
            "理解每个特性由什么机制保证",
            "能够举例说明事务的应用场景"
        ],
        "tips": [
            "原子性由恢复机制保证，一致性由完整性约束保证",
            "隔离性由并发控制机制保证，持久性由恢复机制保证",
            "事务是数据库并发控制和恢复的基本单位"
        ],
        "faq": [
            {"question": "事务的ACID特性分别由什么机制保证？", "answer": "原子性由日志（undo/redo）保证，一致性由完整性约束和应用程序保证，隔离性由锁机制保证，持久性由日志和恢复机制保证。"},
            {"question": "什么是事务的提交和回滚？", "answer": "提交（COMMIT）表示事务成功完成，所有修改永久保存；回滚（ROLLBACK）表示事务失败，撤销所有修改，恢复到事务开始前的状态。"}
        ],
        "image_url": IMG_BASE.format(prompt="transaction ACID properties diagram, atomicity consistency isolation durability with icons and explanations", seed=24)
    },
    "封锁协议与两段锁协议": {
        "detail_content": "封锁是实现并发控制的主要方法。基本锁类型有排他锁（X锁/写锁）和共享锁（S锁/读锁）。封锁协议规定了何时加锁、持锁时间、何时释放等。两段锁协议（2PL）是保证可串行化的重要协议：所有事务必须分两个阶段对数据项加锁和解锁（扩展阶段只能加锁，收缩阶段只能解锁）。",
        "key_points": ["X锁（排他/写）、S锁（共享/读）", "封锁协议：加锁释放规则", "两段锁协议：扩展阶段+收缩阶段", "保证可串行化"],
        "learning_steps": [
            "理解X锁和S锁的含义和相容矩阵",
            "掌握一级、二级、三级封锁协议",
            "理解两段锁协议的含义",
            "理解两段锁协议与可串行化的关系"
        ],
        "tips": [
            "S锁与S锁相容，S锁与X锁不相容，X锁与任何锁都不相容",
            "两段锁协议中，一旦释放锁就不能再申请任何锁",
            "遵循两段锁协议一定能保证可串行化，但可能导致死锁"
        ],
        "faq": [
            {"question": "S锁和X锁有什么区别？", "answer": "S锁（共享锁）允许其他事务读但不允许写；X锁（排他锁）不允许其他事务读和写。读操作加S锁，写操作加X锁。"},
            {"question": "两段锁协议为什么能保证可串行化？", "answer": "两段锁协议确保事务的锁操作分两个阶段，使得并发事务的执行可以等价于某种串行执行顺序，从而保证可串行化。"}
        ],
        "image_url": IMG_BASE.format(prompt="locking protocol and two phase locking diagram, shared lock exclusive lock compatibility matrix, 2PL expansion shrink phases", seed=25)
    },
    "可串行化调度与冲突可串行化": {
        "detail_content": "可串行化调度是指并发事务的执行结果与按某一次序串行执行这些事务的结果相同。冲突可串行化是更严格的概念：如果一个调度可以通过交换不冲突操作的次序得到一个串行调度，则称该调度是冲突可串行化的。冲突操作是指不同事务对同一数据的读写（RW、WR、WW）操作。",
        "key_points": ["可串行化：结果等价于串行", "冲突操作：RW/WR/WW", "冲突可串行化：交换不冲突操作得到串行", "冲突可串行化⇒可串行化"],
        "learning_steps": [
            "理解可串行化的定义",
            "掌握冲突操作的判定",
            "理解冲突可串行化的判定方法（优先图/前趋图）",
            "理解可串行化与冲突可串行化的关系"
        ],
        "tips": [
            "冲突可串行化一定是可串行化的，但反之不一定",
            "判定冲突可串行化可以画优先图，无环则冲突可串行化",
            "可串行化是并发事务正确性的准则"
        ],
        "faq": [
            {"question": "冲突操作有哪些？", "answer": "冲突操作包括：读写（RW）、写读（WR）、写写（WW）。读读（RR）不冲突。冲突操作不能交换次序。"},
            {"question": "如何判断一个调度是否冲突可串行化？", "answer": "画优先图：事务为节点，若Ti的操作与Tj的操作冲突且Ti在Tj之前，则画Ti→Tj的边。若图无环，则调度冲突可串行化。"}
        ],
        "image_url": IMG_BASE.format(prompt="serializability and conflict serializability diagram, precedence graph cycle detection, transaction scheduling", seed=26)
    },
    "多版本并发控制（MVCC）": {
        "detail_content": "多版本并发控制（MVCC）是一种并发控制方法，通过为数据维护多个版本来实现读写不冲突。读操作读取数据的历史版本（快照），写操作创建新版本。MVCC提高了并发度，读操作不需要加锁。InnoDB存储引擎使用MVCC实现了可重复读和读已提交隔离级别。",
        "key_points": ["多版本：数据有多个版本", "读不加锁，读写不冲突", "快照读读取历史版本", "InnoDB默认使用"],
        "learning_steps": [
            "理解MVCC的基本思想",
            "掌握MVCC的实现机制（隐藏列、undo日志、ReadView）",
            "理解快照读和当前读的区别",
            "理解MVCC在不同隔离级别下的行为"
        ],
        "tips": [
            "MVCC通过隐藏列（DB_TRX_ID、DB_ROLL_PTR）和undo日志实现",
            "ReadView决定可见性，不同隔离级别生成ReadView的时机不同",
            "MVCC只对快照读有效，当前读（SELECT FOR UPDATE等）仍需加锁"
        ],
        "faq": [
            {"question": "MVCC如何解决读写冲突？", "answer": "MVCC为每个数据维护多个版本，读操作读取合适的历史版本（快照），不与写操作冲突，实现了读写不阻塞。"},
            {"question": "MVCC和锁有什么关系？", "answer": "MVCC用于读操作（快照读），不需要加锁；写操作和当前读仍需要加锁。MVCC和锁配合使用，提高并发性能。"}
        ],
        "image_url": IMG_BASE.format(prompt="MVCC multi version concurrency control diagram, data versions snapshot read, InnoDB implementation with undo log", seed=27)
    },
    "死锁的处理与预防": {
        "detail_content": "死锁是指两个或多个事务互相等待对方释放锁，导致都无法继续执行的状态。死锁的处理方法包括：预防（破坏死锁的四个必要条件：互斥、请求与保持、不剥夺、循环等待）、检测与解除（检测到死锁后选择一个事务回滚）、超时（事务等待超过一定时间自动回滚）。",
        "key_points": ["死锁：互相等待无法推进", "四个必要条件", "预防：破坏必要条件", "检测与解除：回滚事务", "超时：自动回滚"],
        "learning_steps": [
            "理解死锁的定义和产生条件",
            "掌握死锁的四个必要条件（互斥、请求与保持、不剥夺、循环等待）",
            "掌握死锁的预防方法",
            "掌握死锁的检测与解除方法"
        ],
        "tips": [
            "预防死锁通常采用一次封锁法或顺序封锁法",
            "死锁检测可用等待图，有环则死锁",
            "解除死锁选择代价最小的事务回滚"
        ],
        "faq": [
            {"question": "死锁的四个必要条件是什么？", "answer": "互斥条件、请求与保持条件、不剥夺条件、循环等待条件。破坏其中任一条件即可预防死锁。"},
            {"question": "如何检测和解除死锁？", "answer": "检测：维护等待图，若有环则存在死锁。解除：选择一个或多个事务回滚，释放其持有的锁。"}
        ],
        "image_url": IMG_BASE.format(prompt="deadlock detection and prevention diagram, transaction circular wait, four necessary conditions and solutions", seed=28)
    },
    "数据库的恢复技术": {
        "detail_content": "数据库恢复是指在故障发生后，将数据库从错误状态恢复到已知正确状态的技术。故障类型包括：事务故障、系统故障、介质故障。恢复技术基于日志（Log）：事务开始时写BEGIN日志，修改数据前写更新日志（redo/undo信息），事务结束时写COMMIT日志。恢复时使用REDO（重做已提交事务）和UNDO（撤销未提交事务）。",
        "key_points": ["日志是恢复的基础", "REDO：重做已提交事务", "UNDO：撤销未提交事务", "故障类型：事务/系统/介质"],
        "learning_steps": [
            "理解数据库故障的类型",
            "掌握日志的类型和恢复原则",
            "掌握事务故障、系统故障的恢复方法",
            "掌握介质故障的恢复方法（备份+日志）"
        ],
        "tips": [
            "日志必须先写盘（Write-Ahead Logging，WAL原则）",
            "系统故障恢复：正向扫描日志REDO，反向扫描UNDO",
            "介质故障需要使用数据库备份和日志备份恢复"
        ],
        "faq": [
            {"question": "什么是WAL原则？", "answer": "WAL（Write-Ahead Logging）原则是指在写数据页之前，必须先写日志。这样可以保证故障发生时，能够通过日志恢复数据。"},
            {"question": "REDO和UNDO有什么区别？", "answer": "REDO重做已提交事务的修改（正向扫描日志），UNDO撤销未提交事务的修改（反向扫描日志）。两者配合使用完成故障恢复。"}
        ],
        "image_url": IMG_BASE.format(prompt="database recovery techniques diagram, redo undo operations, transaction system media failure recovery process", seed=29)
    }
}


def main():
    print("开始扩充知识点内容...")
    count = 0
    for content, data in ENRICHMENT.items():
        kp = db.query(KnowledgePoint).filter(KnowledgePoint.content == content).first()
        if kp:
            kp.detail_content = data["detail_content"]
            kp.key_points = data["key_points"]
            kp.learning_steps = data["learning_steps"]
            kp.tips = data["tips"]
            kp.faq = data["faq"]
            kp.image_url = data["image_url"]
            count += 1
            print(f"  更新: {content}")
        else:
            print(f"  未找到: {content}")
    db.commit()
    print(f"\n完成！共更新 {count} 个知识点")


if __name__ == "__main__":
    main()
