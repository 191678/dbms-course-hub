"""简化版Mermaid模板 - 移除init指令，避免与前端配置冲突"""
import urllib.parse

SIMPLE_MERMAID_TEMPLATES = {
    'bplus_tree': {
        'title': 'B+树索引结构',
        'script': '''graph TD
    A([根节点]) --> B[中间节点]
    A --> C[中间节点]
    B --> D((叶子节点))
    B --> E((叶子节点))
    C --> F((叶子节点))
    C --> G((叶子节点))
    D -->|链表| E -->|链表| F -->|链表| G
'''
    },
    'er_diagram': {
        'title': 'ER模型图',
        'script': '''erDiagram
    STUDENT ||--o{ ENROLLS_IN : "注册"
    COURSE ||--o{ ENROLLS_IN : "被注册"
    STUDENT {
        int id PK
        string name
        string email
        date birthdate
    }
    COURSE {
        int id PK
        string name
        int credits
    }
    ENROLLS_IN {
        int student_id FK
        int course_id FK
        date enroll_date
        string grade
    }
'''
    },
    'deadlock': {
        'title': '死锁形成过程',
        'script': '''graph TD
    A[事务T1] --> B[持有锁L1]
    A --> C{请求锁L2}
    B --> D[等待中...]
    E[事务T2] --> F[持有锁L2]
    E --> G{请求锁L1}
    F --> H[等待中...]
    C --> I((死锁!))
    G --> I
'''
    },
    'mvcc_version': {
        'title': 'MVCC版本链',
        'script': '''graph LR
    A[数据行] --> B[版本1: txn=1, data=value1]
    B --> C[版本2: txn=2, data=value2]
    C --> D[版本3: txn=3, data=value3]
    D --> E[版本4: txn=4, data=value4]
    T2[(事务2)] -.->|读取| C
'''
    },
    'acid': {
        'title': '事务ACID特性',
        'script': '''graph TD
    A[事务] --> B[原子性 Atomicity]
    A --> C[一致性 Consistency]
    A --> D[隔离性 Isolation]
    A --> E[持久性 Durability]
    B --> F[要么全部执行\n要么全部回滚]
    C --> G[从一个有效状态\n转移到另一个有效状态]
    D --> H[事务之间相互隔离]
    E --> I[提交后永久保存]
'''
    },
    'database_system': {
        'title': '数据库系统结构',
        'script': '''graph TD
    subgraph "数据库系统组成"
        A[数据库]
        B[数据库管理系统 DBMS]
        C[应用程序]
        D[数据库管理员 DBA]
    end
    subgraph "DBMS核心组件"
        B1[查询处理器]
        B2[存储管理器]
        B3[事务管理器]
    end
    B --> B1
    B --> B2
    B --> B3
    C --> B
    B --> A
    D --> B
'''
    },
    'data_model': {
        'title': '数据模型分类',
        'script': '''graph TD
    A[数据模型三要素] --> B[概念模型]
    A --> C[逻辑模型]
    A --> D[物理模型]
    B --> B1[ER模型]
    C --> C1[层次模型]
    C --> C2[网状模型]
    C --> C3[关系模型]
'''
    },
    'concurrency_problems': {
        'title': '并发操作问题',
        'script': '''graph TD
    A[并发操作问题] --> B[脏读]
    A --> C[不可重复读]
    A --> D[幻读]
    B --> B1[读取了未提交的数据]
    C --> C1[同一事务内两次读取结果不一致]
    D --> D1[同一事务内两次查询返回行数不同]
'''
    },
    'transaction_isolation': {
        'title': '事务隔离级别',
        'script': '''graph TB
    A[READ UNCOMMITTED] --> B[脏读]
    A --> C[不可重复读]
    A --> D[幻读]
    E[READ COMMITTED] --> C
    E --> D
    F[REPEATABLE READ] --> D
    G[SERIALIZABLE]
'''
    },
    'lock_types': {
        'title': '锁的类型',
        'script': '''graph TD
    A[封锁类型] --> B[共享锁 S锁]
    A --> C[排他锁 X锁]
    B --> B1[多个事务可同时持有]
    B --> B2[仅允许读操作]
    C --> C1[仅一个事务可持有]
    C --> C2[允许读写操作]
'''
    },
    'two_phase_lock': {
        'title': '两段锁协议',
        'script': '''graph TD
    A[事务开始] --> B[扩展阶段]
    B --> B1[申请锁]
    B1 --> B2{继续申请?}
    B2 -->|是| B1
    B2 -->|否| C[收缩阶段]
    C --> C1[释放锁]
    C1 --> C2{还有锁?}
    C2 -->|是| C1
    C2 -->|否| D[事务结束]
'''
    },
    'normalization': {
        'title': '数据库范式',
        'script': '''graph TD
    A[第一范式 1NF] --> B[第二范式 2NF]
    B --> C[第三范式 3NF]
    C --> D[BCNF]
    A --> E[原子性: 每个字段不可再分]
    B --> F[消除部分函数依赖]
    C --> G[消除传递依赖]
'''
    },
    'database_recovery': {
        'title': '数据库恢复技术',
        'script': '''graph TD
    A[数据库恢复] --> B[事务故障恢复]
    A --> C[系统故障恢复]
    A --> D[介质故障恢复]
    B --> B1[撤销事务 UNDO]
    C --> C1[UNDO + REDO]
    D --> D1[重装数据库 + REDO]
    A --> E[日志文件]
    A --> F[检查点]
    A --> G[数据库转储]
'''
    },
    'index_structure': {
        'title': '索引结构对比',
        'script': '''graph TD
    subgraph "聚集索引"
        A[主键索引] --> B[叶子节点包含完整数据]
    end
    subgraph "非聚集索引"
        C[二级索引] --> D[叶子节点包含主键]
        D --> A
    end
    subgraph "覆盖索引"
        E[包含所有查询字段] --> F[无需回表]
    end
'''
    },
    'sql_statements': {
        'title': 'SQL语句分类',
        'script': '''graph TD
    A[SQL结构化查询语言] --> B[数据定义语言 DDL]
    A --> C[数据操纵语言 DML]
    A --> D[数据查询语言 DQL]
    A --> E[数据控制语言 DCL]
    B --> B1[CREATE]
    B --> B2[ALTER]
    B --> B3[DROP]
    C --> C1[INSERT]
    C --> C2[UPDATE]
    C --> C3[DELETE]
    D --> D1[SELECT]
    E --> E1[GRANT]
    E --> E2[REVOKE]
'''
    },
    'database_security': {
        'title': '数据库安全性',
        'script': '''graph TD
    A[数据库安全性] --> B[用户标识与鉴别]
    A --> C[存取控制]
    A --> D[视图机制]
    A --> E[审计]
    A --> F[数据加密]
    C --> C1[自主存取控制 DAC]
    C --> C2[强制存取控制 MAC]
'''
    },
    'database_integrity': {
        'title': '数据库完整性',
        'script': '''graph TD
    A[数据库完整性] --> B[实体完整性]
    A --> C[参照完整性]
    A --> D[用户定义完整性]
    B --> B1[主键非空]
    B --> B2[主键唯一]
    C --> C1[外键约束]
'''
    },
    'dependency_normalization': {
        'title': '数据依赖与规范化',
        'script': '''graph TD
    A[数据依赖] --> B[函数依赖]
    A --> C[多值依赖]
    A --> D[连接依赖]
    B --> B1[完全函数依赖]
    B --> B2[部分函数依赖]
    B --> B3[传递函数依赖]
    E[规范化] --> F[1NF]
    F --> G[2NF]
    G --> H[3NF]
    H --> I[BCNF]
'''
    },
    'transaction_state': {
        'title': '事务状态转换',
        'script': '''graph TD
    A[活动状态] --> B[部分提交状态]
    B --> C[失败状态]
    B --> D[提交状态]
    A --> C
    C --> E[中止状态]
    E --> A
'''
    },
    'lock_protocol': {
        'title': '锁协议流程图',
        'script': '''flowchart TD
    A[事务开始] --> B{需要修改数据?}
    B -->|是| C[获取排他锁X]
    B -->|否| D[获取共享锁S]
    C --> E[修改数据]
    D --> F[读取数据]
    E --> G[提交事务]
    F --> G
    G --> H[释放锁]
    H --> I[事务结束]
'''
    },
    'join_types': {
        'title': 'JOIN类型对比',
        'script': '''graph TD
    subgraph "INNER JOIN"
        A[交集部分]
    end
    subgraph "LEFT JOIN"
        B[左表全部 + 右表匹配]
    end
    subgraph "RIGHT JOIN"
        C[右表全部 + 左表匹配]
    end
    subgraph "FULL OUTER JOIN"
        D[两表全部记录]
    end
'''
    },
    'concurrency_control': {
        'title': '并发控制机制',
        'script': '''graph TD
    A[并发请求] --> B{乐观锁}
    A --> C{悲观锁}
    B --> D[版本号检查]
    D -->|版本一致| E[更新成功]
    D -->|版本冲突| F[重试]
    C --> G[获取锁]
    G -->|获取成功| H[执行操作]
    G -->|获取失败| I[等待]
'''
    },
    'three_level_schema': {
        'title': '三级模式二级映像',
        'script': '''graph TD
    subgraph "外模式 (External Schema)"
        A[用户视图1]
        B[用户视图2]
        C[用户视图3]
    end
    subgraph "概念模式 (Conceptual Schema)"
        D[(全局逻辑结构)]
    end
    subgraph "内模式 (Internal Schema)"
        E[存储结构]
        F[索引组织]
        G[数据压缩]
    end
    A -->|外模式/概念模式映像| D
    B -->|外模式/概念模式映像| D
    C -->|外模式/概念模式映像| D
    D -->|概念模式/内模式映像| E
    D -->|概念模式/内模式映像| F
    D -->|概念模式/内模式映像| G
'''
    },
    'select_statement': {
        'title': 'SELECT查询语句结构',
        'script': '''graph TD
    A[SELECT语句] --> B[SELECT子句]
    A --> C[FROM子句]
    A --> D[WHERE子句]
    A --> E[GROUP BY子句]
    A --> F[HAVING子句]
    A --> G[ORDER BY子句]
    A --> H[LIMIT子句]
    B --> B1[指定查询列]
    B --> B2[DISTINCT去重]
    B --> B3[聚合函数]
    C --> C1[表名/视图]
    C --> C2[JOIN连接]
    D --> D1[条件筛选]
    D --> D2[比较运算符]
    D --> D3[逻辑运算符]
    E --> E1[分组列]
    F --> F1[组条件筛选]
    G --> G1[排序方式]
    G --> G2[ASC升序]
    G --> G3[DESC降序]
'''
    },
    'relational_algebra': {
        'title': '关系代数运算',
        'script': '''graph TD
    A[关系代数] --> B[传统集合运算]
    A --> C[专门的关系运算]
    B --> B1[并 Union]
    B --> B2[差 Difference]
    B --> B3[交 Intersection]
    B --> B4[笛卡尔积]
    C --> C1[选择 Selection]
    C --> C2[投影 Projection]
    C --> C3[连接 Join]
    C --> C4[除运算 Division]
    C3 --> C3a[等值连接]
    C3 --> C3b[自然连接]
    C3 --> C3c[外连接]
'''
    },
    'database_design': {
        'title': '数据库设计步骤',
        'script': '''graph TD
    A[需求分析] --> B[概念结构设计]
    B --> C[逻辑结构设计]
    C --> D[物理结构设计]
    D --> E[数据库实施]
    E --> F[数据库运行维护]
    B --> B1[E-R模型]
    C --> C1[关系模式]
    C --> C2[规范化]
    D --> D1[存储结构]
    D --> D2[存取方法]
'''
    },
    'query_optimization': {
        'title': '查询优化过程',
        'script': '''graph TD
    A[SQL查询] --> B[查询分析]
    B --> C[查询检查]
    C --> D[查询优化]
    D --> E[查询执行]
    D --> D1[代数优化]
    D --> D2[物理优化]
    D1 --> D1a[选择运算先做]
    D1 --> D1b[投影运算先做]
    D1 --> D1c[笛卡尔积转连接]
    D2 --> D2a[基于规则优化]
    D2 --> D2b[基于代价优化]
'''
    },
    'transaction_concurrency': {
        'title': '事务与并发控制体系',
        'script': '''graph TD
    A[事务] --> B[ACID特性]
    A --> C[并发控制]
    B --> B1[原子性]
    B --> B2[一致性]
    B --> B3[隔离性]
    B --> B4[持久性]
    C --> D[封锁机制]
    C --> E[死锁处理]
    C --> F[隔离级别]
    D --> D1[共享锁S]
    D --> D2[排他锁X]
    D --> D3[两段锁协议]
    E --> E1[死锁预防]
    E --> E2[死锁检测]
    F --> F1[读未提交]
    F --> F2[读已提交]
    F --> F3[可重复读]
    F --> F4[串行化]
'''
    },
    'database_security_full': {
        'title': '数据库安全性控制',
        'script': '''graph TD
    A[数据库安全性] --> B[用户标识与鉴别]
    A --> C[存取控制]
    A --> D[视图机制]
    A --> E[审计]
    A --> F[数据加密]
    C --> C1[自主存取控制DAC]
    C --> C2[强制存取控制MAC]
    C1 --> C1a[GRANT授权]
    C1 --> C1b[REVOKE收权]
    C2 --> C2a[主体敏感度标记]
    C2 --> C2b[客体敏感度标记]
    B --> B1[静态鉴别]
    B --> B2[动态鉴别]
'''
    },
    'er_to_relation': {
        'title': 'E-R模型转关系模式',
        'script': '''graph TD
    A[E-R模型转换] --> B[实体型转换]
    A --> C[联系型转换]
    B --> B1[实体属性转关系属性]
    B --> B2[实体码转关系码]
    C --> D[1:1联系]
    C --> E[1:n联系]
    C --> F[m:n联系]
    D --> D1[可与任一端合并]
    E --> E1[与n端合并]
    F --> F1[独立关系模式]
    F --> F2[两端实体码为码]
'''
    },
    'normalization_process': {
        'title': '规范化过程与范式',
        'script': '''graph TD
    A[1NF 第一范式] --> B[2NF 第二范式]
    B --> C[3NF 第三范式]
    C --> D[BCNF 巴斯范式]
    D --> E[4NF 第四范式]
    A --> A1[属性不可再分]
    B --> B1[消除部分函数依赖]
    C --> C1[消除传递函数依赖]
    D --> D1[消除主属性传递依赖]
    E --> E1[消除非平凡多值依赖]
    F[数据依赖] --> F1[函数依赖]
    F --> F2[多值依赖]
'''
    },
    'sql_data_types': {
        'title': 'SQL数据类型与约束',
        'script': '''graph TD
    A[SQL数据定义] --> B[数据类型]
    A --> C[完整性约束]
    B --> B1[数值类型]
    B --> B2[字符串类型]
    B --> B3[日期时间类型]
    B1 --> B1a[INT INTEGER]
    B1 --> B1b[FLOAT REAL]
    B1 --> B1c[DECIMAL NUMERIC]
    B2 --> B2a[CHAR]
    B2 --> B2b[VARCHAR]
    B3 --> B3a[DATE]
    B3 --> B3b[TIME]
    C --> C1[NOT NULL]
    C --> C2[UNIQUE]
    C --> C3[PRIMARY KEY]
    C --> C4[FOREIGN KEY]
    C --> C5[CHECK]
'''
    }
}


def generate_mermaid_script_simple(knowledge_point_content, question_text: str = "") -> dict:
    if hasattr(knowledge_point_content, 'content'):
        content = knowledge_point_content.content.lower()
    else:
        content = str(knowledge_point_content).lower()
    lower_question = question_text.lower() if question_text else ""
    combined_text = content + " " + lower_question

    if any(keyword in combined_text for keyword in ['select语句', 'select查询', '查询语句', 'select子句', 'select']):
        template = SIMPLE_MERMAID_TEMPLATES['select_statement']
    elif any(keyword in combined_text for keyword in ['b+树', 'b树']):
        template = SIMPLE_MERMAID_TEMPLATES['bplus_tree']
    elif any(keyword in combined_text for keyword in ['er模型转换', 'e-r模型转', 'er转关系', 'e-r转', '概念模型转']):
        template = SIMPLE_MERMAID_TEMPLATES['er_to_relation']
    elif any(keyword in combined_text for keyword in ['er图', '实体', '概念模型']):
        template = SIMPLE_MERMAID_TEMPLATES['er_diagram']
    elif any(keyword in combined_text for keyword in ['关系代数', '选择运算', '投影运算', '笛卡尔积', '连接运算', '除运算']):
        template = SIMPLE_MERMAID_TEMPLATES['relational_algebra']
    elif '死锁' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['deadlock']
    elif 'mvcc' in combined_text or '版本链' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['mvcc_version']
    elif '两段锁' in combined_text or '2pl' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['two_phase_lock']
    elif '锁的类型' in combined_text or '共享锁' in combined_text or '排他锁' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['lock_types']
    elif '并发操作' in combined_text or '脏读' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['concurrency_problems']
    elif '事务隔离' in combined_text or '隔离级别' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['transaction_isolation']
    elif '事务状态' in combined_text or '状态转换' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['transaction_state']
    elif 'acid' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['acid']
    elif any(keyword in combined_text for keyword in ['三级模式', '二级映像', '二级映象', '外模式', '概念模式', '内模式']):
        template = SIMPLE_MERMAID_TEMPLATES['three_level_schema']
    elif '数据库系统' in combined_text or 'dbms' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['database_system']
    elif '数据模型' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['data_model']
    elif any(keyword in combined_text for keyword in ['查询优化', 'sql优化', '代数优化', '物理优化']):
        template = SIMPLE_MERMAID_TEMPLATES['query_optimization']
    elif any(keyword in combined_text for keyword in ['数据库设计', '概念结构设计', '逻辑结构设计', '物理结构设计', '需求分析']):
        template = SIMPLE_MERMAID_TEMPLATES['database_design']
    elif any(keyword in combined_text for keyword in ['安全性', '存取控制', 'grant', 'revoke', '自主存取', '强制存取', 'dac', 'mac']):
        template = SIMPLE_MERMAID_TEMPLATES['database_security_full']
    elif '完整性' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['database_integrity']
    elif any(keyword in combined_text for keyword in ['数据类型', 'sql数据定义', 'create table', '约束', 'not null', 'primary key', 'foreign key']):
        template = SIMPLE_MERMAID_TEMPLATES['sql_data_types']
    elif 'sql' in combined_text or 'ddl' in combined_text or 'dml' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['sql_statements']
    elif '恢复' in combined_text or '日志' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['database_recovery']
    elif '数据依赖' in combined_text or '函数依赖' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['dependency_normalization']
    elif '范式' in combined_text or '规范化' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['normalization_process']
    elif '索引' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['index_structure']
    elif 'join' in combined_text or '连接' in combined_text:
        template = SIMPLE_MERMAID_TEMPLATES['join_types']
    elif any(keyword in combined_text for keyword in ['事务', '并发控制']):
        template = SIMPLE_MERMAID_TEMPLATES['transaction_concurrency']
    elif any(keyword in combined_text for keyword in ['锁', '协议']):
        template = SIMPLE_MERMAID_TEMPLATES['lock_protocol']
    else:
        return None

    return {
        "media_type": "image",
        "format": "mermaid",
        "content": template['script'],
        "title": template['title']
    }


def generate_image_url(knowledge_point_content, question_text: str) -> dict:
    if hasattr(knowledge_point_content, 'content'):
        content = knowledge_point_content.content
    else:
        content = str(knowledge_point_content)
    prompt_en = f"Educational infographic about {content}, flat design, light green background, blue green color scheme, professional illustration, ultra high resolution, 4K quality, detailed diagram with clear text, large bold text labels filling the entire image, high contrast, content fills full canvas, readable from distance"

    if '比喻' in question_text or '例子' in question_text:
        prompt_en = f"Creative illustration explaining {content} using metaphor, colorful, engaging, educational style, flat design, ultra high resolution, 4K quality, detailed artwork, large prominent text, fills entire canvas"
    elif '概念' in content:
        prompt_en = f"Concept diagram of {content}, clean modern design, tech infographic, professional layout, ultra high resolution, 4K quality, large bold readable text labels, sharp details, fills full canvas"

    encoded_prompt = urllib.parse.quote(prompt_en)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=2560&height=1440"

    return {
        "media_type": "image",
        "format": "url",
        "content": image_url,
        "title": content
    }
