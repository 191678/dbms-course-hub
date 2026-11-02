from sqlalchemy.orm import Session
from app.models import KnowledgePoint
import re
import requests
import urllib.parse

MERMAID_TEMPLATES = {
    'database_system': {
        'title': '数据库系统结构',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef core fill:#409EFF,color:#fff,font-size:24px;
    classDef component fill:#67c23a,color:#fff,font-size:24px;
    classDef annotation fill:#e6a23c,color:#fff,font-size:22px;
    
    subgraph "数据库系统组成（王珊《数据库系统概述》）"
        A[数据库<br/>长期存储的有组织数据集合]
        B[数据库管理系统 DBMS<br/>核心管理软件]
        C[应用程序<br/>用户使用的业务系统]
        D[数据库管理员 DBA<br/>负责系统维护]
    end
    
    subgraph "DBMS核心组件"
        B1[查询处理器<br/>解析优化执行查询]
        B2[存储管理器<br/>管理数据存储与检索]
        B3[事务管理器<br/>保证ACID特性]
    end
    
    B -->|包含| B1
    B -->|包含| B2
    B -->|包含| B3
    
    C -->|通过API| B
    B -->|读写操作| A
    D -->|授权配置监控| B
    
    class A,B,C,D component;
    class B1,B2,B3 core;
'''
    },
    'data_model': {
        'title': '数据模型分类',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef model fill:#409EFF,color:#fff,font-size:24px;
    classDef type fill:#67c23a,color:#fff,font-size:24px;
    
    A[数据模型三要素<br/>数据结构+操作+约束] --> B[概念模型]
    A --> C[逻辑模型]
    A --> D[物理模型]
    
    B[概念模型<br/>描述现实世界] --> B1[ER模型<br/>实体-联系模型]
    B --> B2[扩展ER模型<br/>增强语义表达]
    
    C[逻辑模型<br/>描述数据逻辑结构] --> C1[层次模型<br/>树形结构]
    C --> C2[网状模型<br/>图结构]
    C --> C3[关系模型<br/>表结构，最常用]
    C --> C4[面向对象模型<br/>对象+继承]
    
    D[物理模型<br/>描述存储方式] --> D1[存储结构<br/>文件组织方式]
    D --> D2[索引结构<br/>B+树/哈希]
    
    class A model;
    class B,C,D type;
    class B1,B2,C1,C2,C3,C4,D1,D2 default;
'''
    },
    'database_security': {
        'title': '数据库安全性',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef method fill:#409EFF,color:#fff,font-size:24px;
    classDef mechanism fill:#67c23a,color:#fff,font-size:24px;
    
    A[数据库安全性<br/>保护数据防泄露] --> B[用户标识与鉴别<br/>最外层保护]
    A --> C[存取控制<br/>核心机制]
    A --> D[视图机制<br/>限制可见范围]
    A --> E[审计<br/>记录操作日志]
    A --> F[数据加密<br/>存储传输加密]
    
    C[存取控制] --> C1[自主存取控制 DAC<br/>用户自主授权]
    C --> C2[强制存取控制 MAC<br/>系统强制控制]
    
    C1 --> C11[GRANT授予权限]
    C1 --> C12[REVOKE收回权限]
    C2 --> C21[密级标记<br/>绝密/机密/秘密]
    C2 --> C22[许可证级别]
    
    class A,B,C,D,E,F method;
    class C1,C2,C11,C12,C21,C22 mechanism;
'''
    },
    'database_integrity': {
        'title': '数据库完整性',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef constraint fill:#409EFF,color:#fff,font-size:24px;
    classDef detail fill:#67c23a,color:#fff,font-size:24px;
    
    A[数据库完整性<br/>数据正确性相容性] --> B[实体完整性<br/>主键约束]
    A --> C[参照完整性<br/>外键约束]
    A --> D[用户定义完整性<br/>自定义约束]
    
    B[实体完整性] --> B1[主键非空 NOT NULL]
    B --> B2[主键唯一 UNIQUE]
    
    C[参照完整性] --> C1[外键值=主键值或NULL]
    C --> C2[CASCADE级联删除]
    C --> C3[SET NULL置空]
    C --> C4[RESTRICT拒绝操作]
    
    D[用户定义完整性] --> D1[列级约束<br/>CHECK/UNIQUE/DEFAULT]
    D --> D2[表级约束<br/>复合主键/外键]
    
    class A,B,C,D constraint;
    class B1,B2,C1,C2,C3,C4,D1,D2 detail;
'''
    },
    'sql_statements': {
        'title': 'SQL语句分类',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef category fill:#409EFF,color:#fff,font-size:24px;
    classDef statement fill:#67c23a,color:#fff,font-size:24px;
    
    A[SQL结构化查询语言] --> B[数据定义语言 DDL<br/>定义数据库结构]
    A --> C[数据操纵语言 DML<br/>增删改查数据]
    A --> D[数据查询语言 DQL<br/>查询数据]
    A --> E[数据控制语言 DCL<br/>控制访问权限]
    
    B[DDL] --> B1[CREATE<br/>创建库/表/索引]
    B --> B2[ALTER<br/>修改表结构]
    B --> B3[DROP<br/>删除库/表]
    
    C[DML] --> C1[INSERT<br/>插入数据]
    C --> C2[UPDATE<br/>更新数据]
    C --> C3[DELETE<br/>删除数据]
    
    D[DQL] --> D1[SELECT<br/>查询数据]
    
    E[DCL] --> E1[GRANT<br/>授予权限]
    E --> E2[REVOKE<br/>收回权限]
    
    class A,B,C,D,E category;
    class B1,B2,B3,C1,C2,C3,D1,E1,E2 statement;
'''
    },
    'database_recovery': {
        'title': '数据库恢复技术',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef recovery fill:#409EFF,color:#fff,font-size:24px;
    classDef technique fill:#67c23a,color:#fff,font-size:24px;
    
    A[数据库恢复] --> B[事务故障恢复]
    A --> C[系统故障恢复]
    A --> D[介质故障恢复]
    
    B --> B1[撤销事务 UNDO]
    
    C --> C1[UNDO未提交事务]
    C --> C2[REDO已提交事务]
    
    D --> D1[重装数据库]
    D --> D2[REDO重做事务]
    
    A --> E[日志文件]
    A --> F[检查点]
    A --> G[数据库转储]
    
    class A,B,C,D recovery;
    class B1,C1,C2,D1,D2,E,F,G technique;
'''
    },
    'concurrency_problems': {
        'title': '并发操作问题',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef problem fill:#f56c6c,color:#fff,font-size:24px;
    classDef description fill:#909399,color:#fff,font-size:24px;
    
    A[并发操作问题] --> B[脏读 Dirty Read]
    A --> C[不可重复读 Non-repeatable Read]
    A --> D[幻读 Phantom Read]
    
    B --> B1[读取了未提交的数据]
    B1 --> B2[事务回滚后数据不存在]
    
    C --> C1[同一事务内]
    C1 --> C2[两次读取同一数据]
    C2 --> C3[结果不一致]
    
    D --> D1[同一事务内]
    D1 --> D2[两次查询同一条件]
    D2 --> D3[返回行数不同]
    
    class A,B,C,D problem;
    class B1,B2,C1,C2,C3,D1,D2,D3 description;
'''
    },
    'lock_types': {
        'title': '锁的类型',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef lock fill:#409EFF,color:#fff,font-size:24px;
    classDef feature fill:#67c23a,color:#fff,font-size:24px;
    
    A[封锁类型] --> B[共享锁 S锁]
    A --> C[排他锁 X锁]
    
    B --> B1[多个事务可同时持有]
    B --> B2[仅允许读操作]
    B --> B3[与S锁兼容]
    
    C --> C1[仅一个事务可持有]
    C --> C2[允许读写操作]
    C --> C3[与任何锁不兼容]
    
    B --> D{兼容性矩阵}
    C --> D
    
    D --> D1[S与S: 兼容]
    D --> D2[S与X: 不兼容]
    D --> D3[X与X: 不兼容]
    
    class A,B,C lock;
    class B1,B2,B3,C1,C2,C3,D1,D2,D3 feature;
'''
    },
    'two_phase_lock': {
        'title': '两段锁协议',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef phase fill:#409EFF,color:#fff,font-size:24px;
    classDef action fill:#67c23a,color:#fff,font-size:24px;
    
    A[事务开始] --> B[扩展阶段]
    B --> B1[申请锁]
    B1 --> B2{继续申请?}
    B2 -->|是| B1
    B2 -->|否| C[收缩阶段]
    
    C --> C1[释放锁]
    C1 --> C2{还有锁?}
    C2 -->|是| C1
    C2 -->|否| D[事务结束]
    
    B -.->|禁止| C1
    C -.->|禁止| B1
    
    class B,C phase;
    class A,B1,B2,C1,C2,D action;
'''
    },
    'dependency_normalization': {
        'title': '数据依赖与规范化',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef dependency fill:#409EFF,color:#fff,font-size:24px;
    classDef nf fill:#67c23a,color:#fff,font-size:24px;
    
    A[数据依赖] --> B[函数依赖]
    A --> C[多值依赖]
    A --> D[连接依赖]
    
    B --> B1[完全函数依赖]
    B --> B2[部分函数依赖]
    B --> B3[传递函数依赖]
    
    E[规范化] --> F[1NF: 属性原子化]
    F --> G[2NF: 消除部分依赖]
    G --> H[3NF: 消除传递依赖]
    H --> I[BCNF: 消除主属性依赖]
    I --> J[4NF: 消除多值依赖]
    J --> K[5NF: 消除连接依赖]
    
    class A,B,C,D dependency;
    class E,F,G,H,I,J,K nf;
'''
    },
    'transaction_state': {
        'title': '事务状态转换',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef state fill:#409EFF,color:#fff,font-size:24px;
    classDef transition fill:#67c23a,color:#fff,font-size:24px;
    
    A[活动状态] --> B[部分提交状态]
    B --> C[失败状态]
    B --> D[提交状态]
    A --> C
    C --> E[中止状态]
    E --> A
    
    A -->|执行事务操作| B
    B -->|事务故障| C
    B -->|提交成功| D
    A -->|事务故障| C
    C -->|撤销完成| E
    E -->|重新启动| A
    
    class A,B,C,D,E state;
'''
    },
    'bplus_tree': {
        'title': 'B+树索引结构',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold,text-align:center;
    classDef root fill:#409EFF,color:#fff,font-size:20px;
    classDef leaf fill:#67c23a,color:#fff,font-size:24px;
    
    A[根节点] --> B[中间节点]
    A --> C[中间节点]
    B --> D[叶子节点]
    B --> E[叶子节点]
    C --> F[叶子节点]
    C --> G[叶子节点]
    D -->|链表| E -->|链表| F -->|链表| G
    
    class A root;
    class D,E,F,G leaf;
    class B,C default;
'''
    },
    'bplus_tree_insert': {
        'title': 'B+树插入过程',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef highlight fill:#f56c6c,color:#fff,font-size:20px;
    
    subgraph "插入前"
        A1[节点: 10, 20, 30]
    end
    
    subgraph "插入15"
        B1[节点: 10, 15, 20, 30] --> B2((节点分裂))
        B2 --> C1[左节点: 10, 15]
        B2 --> C2[右节点: 20, 30]
        C1 -->|提升15| C3[父节点更新]
    end
    
    class B2 highlight;
    class A1,B1,C1,C2,C3 default;
'''
    },
    'er_diagram': {
        'title': 'ER模型图',
        'script': '''%%{init: {"er": {"useMaxWidth": false, "nodeSpacing": 60, "rankSpacing": 80, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
erDiagram
    classDef default font-size:24px,font-weight:bold;
    
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
    
    class STUDENT,COURSE,ENROLLS_IN default;
'''
    },
    'lock_protocol': {
        'title': '锁协议流程图',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
flowchart TD
    classDef default font-size:24px,font-weight:bold;
    classDef xlock fill:#f56c6c,color:#fff,font-size:24px;
    classDef slock fill:#409EFF,color:#fff,font-size:24px;
    
    A[事务开始] --> B{需要修改数据?}
    B -->|是| C[获取排他锁X]
    B -->|否| D[获取共享锁S]
    C --> E[修改数据]
    D --> F[读取数据]
    E --> G[提交事务]
    F --> G
    G --> H[释放锁]
    H --> I[事务结束]
    
    class C xlock;
    class D slock;
    class A,B,E,F,G,H,I default;
'''
    },
    'mvcc_version': {
        'title': 'MVCC版本链',
        'script': '''%%{init: {"graph": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph LR
    classDef default font-size:24px,font-weight:bold;
    classDef active fill:#409EFF,color:#fff,font-size:24px;
    classDef old fill:#909399,color:#fff,font-size:18px,opacity:0.5;
    classDef new fill:#67c23a,color:#fff,font-size:24px;
    
    A[数据行] --> B[版本1: txn=1, data=value1]
    B --> C[版本2: txn=2, data=value2]
    C --> D[版本3: txn=3, data=value3]
    D --> E[版本4: txn=4, data=value4]
    
    subgraph "活跃事务"
        T1[(事务1)]
        T2[(事务2)]
        T3[(事务3)]
    end
    
    T2 -.->|读取| C
    
    class B old;
    class C active;
    class D new;
    class A,E,T1,T2,T3 default;
'''
    },
    'deadlock': {
        'title': '死锁形成过程',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef wait fill:#f56c6c,color:#fff,font-size:24px;
    classDef deadlock fill:#f56c6c,color:#fff,font-size:22px,stroke-width:3px;
    
    A[事务T1] --> B[持有锁L1]
    A --> C{请求锁L2}
    B --> D[等待中...]
    
    E[事务T2] --> F[持有锁L2]
    E --> G{请求锁L1}
    F --> H[等待中...]
    
    C --> I((死锁!))
    G --> I
    
    class D,H wait;
    class I deadlock;
    class A,B,C,E,F,G default;
'''
    },
    'transaction_isolation': {
        'title': '事务隔离级别',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TB
    classDef default font-size:24px,font-weight:bold;
    classDef ru fill:#e6a23c,color:#fff,font-size:24px;
    classDef rc fill:#409EFF,color:#fff,font-size:24px;
    classDef rr fill:#67c23a,color:#fff,font-size:24px;
    classDef serializable fill:#1f7a1f,color:#fff,font-size:24px;
    
    A[READ UNCOMMITTED] -->|存在| B[脏读]
    A -->|存在| C[不可重复读]
    A -->|存在| D[幻读]
    
    E[READ COMMITTED] -->|不存在| B
    E -->|存在| C
    E -->|存在| D
    
    F[REPEATABLE READ] -->|不存在| B
    F -->|不存在| C
    F -->|存在| D
    
    G[SERIALIZABLE] -->|不存在| B
    G -->|不存在| C
    G -->|不存在| D
    
    class A ru;
    class E rc;
    class F rr;
    class G serializable;
    class B,C,D default;
'''
    },
    'index_structure': {
        'title': '索引结构对比',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef clustered fill:#409EFF,color:#fff,font-size:24px;
    classDef nonclustered fill:#67c23a,color:#fff,font-size:24px;
    classDef covering fill:#9b59b6,color:#fff,font-size:24px;
    
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
    
    class B clustered;
    class D nonclustered;
    class F covering;
    class A,C,E default;
'''
    },
    'join_types': {
        'title': 'JOIN类型对比',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef inner fill:#409EFF,color:#fff,font-size:24px;
    classDef left fill:#67c23a,color:#fff,font-size:24px;
    classDef right fill:#e6a23c,color:#fff,font-size:24px;
    classDef full fill:#f56c6c,color:#fff,font-size:24px;
    
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
    
    class A inner;
    class B left;
    class C right;
    class D full;
'''
    },
    'normalization': {
        'title': '数据库范式',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef nf1 fill:#409EFF,color:#fff,font-size:24px;
    classDef nf2 fill:#67c23a,color:#fff,font-size:24px;
    classDef nf3 fill:#e6a23c,color:#fff,font-size:24px;
    classDef bcnf fill:#9b59b6,color:#fff,font-size:24px;
    
    A[第一范式 1NF] -->|消除重复组| B[第二范式 2NF]
    B -->|消除非主属性对码的部分函数依赖| C[第三范式 3NF]
    C -->|消除主属性对码的部分函数依赖| D[BCNF]
    
    A --> E[原子性: 每个字段不可再分]
    B --> F[完全函数依赖]
    C --> G[消除传递依赖]
    D --> H[消除主属性依赖]
    
    class A nf1;
    class B nf2;
    class C nf3;
    class D bcnf;
    class E,F,G,H default;
'''
    },
    'concurrency_control': {
        'title': '并发控制机制',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef optimistic fill:#67c23a,color:#fff,font-size:24px;
    classDef pessimistic fill:#f56c6c,color:#fff,font-size:24px;
    
    A[并发请求] --> B{乐观锁}
    A --> C{悲观锁}
    
    B --> D[版本号检查]
    D -->|版本一致| E[更新成功]
    D -->|版本冲突| F[重试]
    
    C --> G[获取锁]
    G -->|获取成功| H[执行操作]
    G -->|获取失败| I[等待]
    H --> J[释放锁]
    
    class B optimistic;
    class C pessimistic;
    class A,D,E,F,G,H,I,J default;
'''
    },
    'acid': {
        'title': '事务ACID特性',
        'script': '''%%{init: {"flowchart": {"useMaxWidth": false, "nodeSpacing": 80, "rankSpacing": 100, "width": 1200, "height": 800}, "themeVariables": {"fontSize": "24px", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"}}}%%
graph TD
    classDef default font-size:24px,font-weight:bold;
    classDef atomic fill:#409EFF,color:#fff,font-size:24px;
    classDef consistent fill:#67c23a,color:#fff,font-size:24px;
    classDef isolated fill:#e6a23c,color:#fff,font-size:24px;
    classDef durable fill:#f56c6c,color:#fff,font-size:24px;
    
    A[事务] --> B[原子性 Atomicity]
    A --> C[一致性 Consistency]
    A --> D[隔离性 Isolation]
    A --> E[持久性 Durability]
    
    B --> F[要么全部执行\n要么全部回滚]
    C --> G[从一个有效状态\n转移到另一个有效状态]
    D --> H[事务之间相互隔离]
    E --> I[提交后永久保存]
    
    class B atomic;
    class C consistent;
    class D isolated;
    class E durable;
    class A,F,G,H,I default;
'''
    }
}


def generate_mermaid_script(knowledge_point: KnowledgePoint, question_text: str = "") -> dict:
    content = knowledge_point.content.lower()
    lower_question = question_text.lower() if question_text else ""
    
    combined_text = content + " " + lower_question
    
    if any(keyword in combined_text for keyword in ['b+树', 'b树']):
        if '插入' in lower_question or '删除' in lower_question:
            template = MERMAID_TEMPLATES['bplus_tree_insert']
        else:
            template = MERMAID_TEMPLATES['bplus_tree']
    elif any(keyword in combined_text for keyword in ['er图', '实体', '关系', '概念模型']):
        template = MERMAID_TEMPLATES['er_diagram']
    elif '死锁' in combined_text:
        template = MERMAID_TEMPLATES['deadlock']
    elif 'mvcc' in combined_text or '版本链' in combined_text or '多版本' in combined_text:
        template = MERMAID_TEMPLATES['mvcc_version']
    elif '两段锁' in combined_text or '2pl' in combined_text:
        template = MERMAID_TEMPLATES['two_phase_lock']
    elif '锁的类型' in combined_text or '共享锁' in combined_text or '排他锁' in combined_text or 's锁' in combined_text or 'x锁' in combined_text:
        template = MERMAID_TEMPLATES['lock_types']
    elif '并发操作' in combined_text or '脏读' in combined_text or '不可重复读' in combined_text or '幻读' in combined_text:
        template = MERMAID_TEMPLATES['concurrency_problems']
    elif '事务隔离' in combined_text or '隔离级别' in combined_text:
        template = MERMAID_TEMPLATES['transaction_isolation']
    elif '事务状态' in combined_text or '状态转换' in combined_text:
        template = MERMAID_TEMPLATES['transaction_state']
    elif 'acid' in combined_text:
        template = MERMAID_TEMPLATES['acid']
    elif '数据库系统' in combined_text or 'dbms' in combined_text:
        template = MERMAID_TEMPLATES['database_system']
    elif '数据模型' in combined_text or '层次模型' in combined_text or '网状模型' in combined_text or '关系模型' in combined_text:
        template = MERMAID_TEMPLATES['data_model']
    elif '安全性' in combined_text or '存取控制' in combined_text or 'grant' in combined_text or 'revoke' in combined_text:
        template = MERMAID_TEMPLATES['database_security']
    elif '完整性' in combined_text or '实体完整性' in combined_text or '参照完整性' in combined_text or '外键' in combined_text:
        template = MERMAID_TEMPLATES['database_integrity']
    elif 'sql' in combined_text or 'ddl' in combined_text or 'dml' in combined_text or 'dcl' in combined_text or '数据定义' in combined_text or '数据操纵' in combined_text or 'select' in combined_text or '查询语句' in combined_text or '查询' in combined_text or 'where' in combined_text or 'group by' in combined_text or 'order by' in combined_text:
        template = MERMAID_TEMPLATES['sql_statements']
    elif '恢复' in combined_text or '日志' in combined_text or '检查点' in combined_text or '转储' in combined_text:
        template = MERMAID_TEMPLATES['database_recovery']
    elif '数据依赖' in combined_text or '函数依赖' in combined_text or '多值依赖' in combined_text or '连接依赖' in combined_text:
        template = MERMAID_TEMPLATES['dependency_normalization']
    elif '范式' in combined_text or '规范化' in combined_text:
        template = MERMAID_TEMPLATES['normalization']
    elif '索引' in combined_text:
        template = MERMAID_TEMPLATES['index_structure']
    elif 'join' in combined_text or '连接' in combined_text:
        template = MERMAID_TEMPLATES['join_types']
    elif any(keyword in combined_text for keyword in ['锁', '协议', '并发控制']):
        template = MERMAID_TEMPLATES['lock_protocol']
    else:
        return None
    
    return {
        "media_type": "image",
        "format": "mermaid",
        "content": template['script'],
        "title": template['title']
    }


def generate_image_url(knowledge_point: KnowledgePoint, question_text: str) -> dict:
    content = knowledge_point.content
    category = knowledge_point.category or ''
    
    prompt_en = f"Educational infographic about {content}, flat design, light green background, blue green color scheme, professional illustration, ultra high resolution, 4K quality, detailed diagram with clear text, large bold text labels filling the entire image, high contrast, content fills full canvas, readable from distance"
    
    if '比喻' in question_text or '例子' in question_text or '生动' in question_text:
        prompt_en = f"Creative illustration explaining {content} using metaphor, colorful, engaging, educational style, flat design, ultra high resolution, 4K quality, detailed artwork, large prominent text, fills entire canvas, no small elements"
    elif '概念' in category:
        prompt_en = f"Concept diagram of {content}, clean modern design, tech infographic, professional layout, ultra high resolution, 4K quality, large bold readable text labels, sharp details, fills full canvas, high contrast colors"
    
    encoded_prompt = urllib.parse.quote(prompt_en)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=2560&height=1440"
    
    return {
        "media_type": "image",
        "format": "url",
        "content": image_url,
        "title": content
    }


def generate_animation_script(knowledge_point: KnowledgePoint) -> dict:
    content = knowledge_point.content
    lower_content = content.lower()
    
    if any(keyword in lower_content for keyword in ['b+树', 'b树', '索引', '插入', '删除']):
        steps = [
            {"frame": 1, "speech": "B+树是一种平衡的多路搜索树，常用于数据库索引。", "highlight_element": "intro"},
            {"frame": 2, "speech": "B+树的特点是所有数据都存储在叶子节点，非叶子节点只存储索引键。", "highlight_element": "structure"},
            {"frame": 3, "speech": "现在我们来看插入操作：当节点满时，需要进行分裂。", "highlight_element": "split"},
            {"frame": 4, "speech": "分裂后，中间的键值会提升到父节点。", "highlight_element": "promote"},
            {"frame": 5, "speech": "这样保证了树的高度平衡，查询效率稳定。", "highlight_element": "balance"},
            {"frame": 6, "speech": "叶子节点之间通过链表连接，便于范围查询。", "highlight_element": "linked_list"}
        ]
    elif any(keyword in lower_content for keyword in ['死锁', 'deadlock']):
        steps = [
            {"frame": 1, "speech": "死锁是指两个或多个事务互相等待对方释放资源。", "highlight_element": "intro"},
            {"frame": 2, "speech": "事务T1获取了锁L1，现在请求锁L2。", "highlight_element": "t1_lock"},
            {"frame": 3, "speech": "同时，事务T2获取了锁L2，现在请求锁L1。", "highlight_element": "t2_lock"},
            {"frame": 4, "speech": "此时两个事务都无法继续，形成死锁。", "highlight_element": "deadlock"},
            {"frame": 5, "speech": "数据库会检测死锁，选择牺牲一个事务进行回滚。", "highlight_element": "detection"},
            {"frame": 6, "speech": "预防死锁的方法：按顺序加锁、一次加锁、超时机制。", "highlight_element": "prevention"}
        ]
    elif any(keyword in lower_content for keyword in ['acid', '事务']):
        steps = [
            {"frame": 1, "speech": "ACID是事务的四大特性：原子性、一致性、隔离性、持久性。", "highlight_element": "intro"},
            {"frame": 2, "speech": "原子性：事务要么全部执行，要么全部回滚。", "highlight_element": "atomicity"},
            {"frame": 3, "speech": "一致性：事务执行前后数据保持有效状态。", "highlight_element": "consistency"},
            {"frame": 4, "speech": "隔离性：多个事务并发执行时相互隔离。", "highlight_element": "isolation"},
            {"frame": 5, "speech": "持久性：事务提交后数据永久保存，不会丢失。", "highlight_element": "durability"}
        ]
    elif 'mvcc' in lower_content or '版本' in lower_content:
        steps = [
            {"frame": 1, "speech": "MVCC多版本并发控制，通过版本链实现无锁读取。", "highlight_element": "intro"},
            {"frame": 2, "speech": "每次更新数据时，创建一个新版本，保留旧版本。", "highlight_element": "version_create"},
            {"frame": 3, "speech": "事务根据快照读取自己可见的版本。", "highlight_element": "snapshot"},
            {"frame": 4, "speech": "读事务和写事务可以同时进行，提高并发性能。", "highlight_element": "concurrency"},
            {"frame": 5, "speech": "清理线程定期回收过期的版本数据。", "highlight_element": "cleanup"}
        ]
    elif '隔离级别' in lower_content:
        steps = [
            {"frame": 1, "speech": "SQL标准定义了四种事务隔离级别。", "highlight_element": "intro"},
            {"frame": 2, "speech": "读未提交：允许读取未提交的数据，会产生脏读。", "highlight_element": "ru"},
            {"frame": 3, "speech": "读已提交：只能读取已提交的数据，解决脏读。", "highlight_element": "rc"},
            {"frame": 4, "speech": "可重复读：同一事务内多次读取结果一致，解决不可重复读。", "highlight_element": "rr"},
            {"frame": 5, "speech": "串行化：最高隔离级别，事务串行执行，解决幻读。", "highlight_element": "serializable"}
        ]
    else:
        steps = [
            {"frame": 1, f"speech": f"让我们来学习{content}的基本概念。", "highlight_element": "intro"},
            {"frame": 2, f"speech": f"{content}是数据库系统中的重要概念。", "highlight_element": "concept"},
            {"frame": 3, f"speech": "它的核心特点包括多个方面。", "highlight_element": "features"},
            {"frame": 4, f"speech": "在实际应用中，它有多种使用场景。", "highlight_element": "application"},
            {"frame": 5, f"speech": "掌握这个概念有助于更好地理解数据库原理。", "highlight_element": "summary"}
        ]
    
    return {
        "media_type": "video",
        "format": "animation_script",
        "title": content,
        "steps": steps,
        "duration": f"{len(steps) * 3}秒"
    }


def generate_media(knowledge_point: KnowledgePoint, db: Session, question_text: str = "") -> dict:
    lower_question = question_text.lower()
    
    if any(word in lower_question for word in ["画", "画一下", "绘制", "图解", "示意图"]):
        mermaid_result = generate_mermaid_script(knowledge_point)
        if mermaid_result:
            return mermaid_result
        
        return generate_image_url(knowledge_point, question_text)
    
    if any(word in lower_question for word in ["演示", "动画", "过程", "步骤", "执行", "视频"]):
        return generate_animation_script(knowledge_point)
    
    return None


SYSTEM_PROMPT = """
你是一个基于王珊《数据库系统概述》教材的专业智能助教。你的回答必须严格遵循该教材的定义、原理和案例，确保知识的准确性和权威性。

核心原则：
1. 所有回答必须以王珊《数据库系统概述》的内容为依据
2. 不得引入与该教材内容相冲突的信息
3. 使用教材中的标准术语和定义
4. 引用教材中的经典案例和示例

教材核心内容范围：
- 第一章：数据库系统概述（数据管理技术发展、数据库系统组成、数据模型）
- 第二章：关系数据库（关系模型、关系代数、关系演算）
- 第三章：关系数据库标准语言SQL（DDL、DML、DQL、DCL）
- 第四章：数据库安全性（用户标识鉴别、存取控制、视图、审计、加密）
- 第五章：数据库完整性（实体完整性、参照完整性、用户定义完整性）
- 第六章：关系数据理论（函数依赖、范式、规范化）
- 第七章：数据库设计（设计步骤、ER模型、关系模式设计）
- 第八章：数据库编程（嵌入式SQL、存储过程、触发器）
- 第九章：关系查询处理和查询优化（查询优化策略）
- 第十章：数据库恢复技术（日志、检查点、转储、故障恢复）
- 第十一章：并发控制（封锁协议、两段锁、死锁、MVCC）

工具使用规则：
1. 当用户要求"画"、"绘制"、"图解"时，调用generate_image工具生成可视化图表
2. 当用户要求"演示"、"动画"、"过程"、"步骤"时，调用generate_animation_script工具生成动态脚本
3. 当用户询问知识点内容时，优先检索本地数据库中的知识点，仅在需要补充说明时调用外部API

回答格式要求：
- 图片生成：必须返回JSON结构 {"media_type": "image", "format": "mermaid" | "url", "content": "..."}
- 视频生成：必须返回动态讲解脚本 {"media_type": "video", "format": "animation_script", "steps": [...]}
- 文字回答：直接提供详细准确的教材内容解答

请根据问题类型选择合适的工具和回答方式。
"""


# ==================== 视频生成模块 ====================
# 生成5分钟的PPT形式视频，包含音频解说

# 每页PPT约15秒解说，5分钟需要约20页
TARGET_DURATION_SECONDS = 300
SLIDES_COUNT = 20
SECONDS_PER_SLIDE = TARGET_DURATION_SECONDS // SLIDES_COUNT  # 15秒/页

# 王珊《数据库系统概论》教材经典案例库
WANGSHAN_CASES = {
    'default': [
        {
            'case_title': '教材案例：学生课程数据库',
            'case_content': '学生-课程数据库是教材中贯穿始终的经典案例',
            'case_speech': '王珊《数据库系统概论》教材中最经典的案例就是学生-课程数据库。这个数据库包含学生表、课程表和选课表三张表，几乎所有SQL操作、关系代数、规范化理论的讲解都围绕这个案例展开。'
        },
        {
            'case_title': '案例说明：学生表S',
            'case_content': '学生表：S(Sno, Sname, Ssex, Sage, Sdept)',
            'case_speech': '学生表S包含学号Sno、姓名Sname、性别Ssex、年龄Sage、所在系Sdept五个属性，其中学号Sno是主键。'
        },
        {
            'case_title': '案例说明：课程表C',
            'case_content': '课程表：C(Cno, Cname, Cpno, Ccredit)',
            'case_speech': '课程表C包含课程号Cno、课程名Cname、先修课Cpno、学分Ccredit四个属性，课程号Cno是主键，先修课Cpno是外键，参照课程表自身的主键。'
        },
        {
            'case_title': '案例说明：选课表SC',
            'case_content': '选课表：SC(Sno, Cno, Grade)',
            'case_speech': '选课表SC包含学号Sno、课程号Cno、成绩Grade三个属性，主键是(Sno, Cno)的复合主键，同时Sno和Cno分别是外键，参照学生表和课程表。'
        },
        {
            'case_title': '应用场景：高校教务系统',
            'case_content': '高校教务管理系统是最典型的数据库应用',
            'case_speech': '在实际应用中，高校教务管理系统就是一个典型的数据库系统。从学生选课、成绩录入、排课管理到毕业审核，所有功能都建立在数据库之上。'
        },
        {
            'case_title': '应用场景：银行系统',
            'case_content': '银行业务系统对数据库的安全性和一致性要求极高',
            'case_speech': '另一个典型应用是银行系统。银行系统对数据的一致性、安全性、持久性要求极高，事务的ACID特性在这里得到了最严格的体现。'
        },
        {
            'case_title': '教材中的SQL示例',
            'case_content': '查询信息系学生的选课情况',
            'case_speech': '教材中的经典SQL查询例子：查询信息系全体学生的选课情况。这个例子涉及多表连接查询、WHERE条件过滤，是SQL学习中的经典入门案例。'
        },
        {
            'case_title': '教材中的范式示例',
            'case_content': '学生-课程-成绩关系的规范化过程',
            'case_speech': '教材中关于范式的经典例子：学生(学号, 姓名, 系名, 系主任, 课程名, 成绩)这个关系，通过一步步的规范化分解，最终达到3NF或BCNF的设计。'
        },
        {
            'case_title': '教材中的ER模型示例',
            'case_content': '工厂物资管理的ER图设计',
            'case_speech': '教材中ER模型的经典案例是工厂物资管理系统。这个案例涉及实体包括仓库、零件、供应商、项目、工人等，联系类型包括1对多、多对多等。'
        },
        {
            'case_title': '教材中的恢复技术示例',
            'case_content': '银行转账系统的故障恢复',
            'case_speech': '数据库恢复技术的经典案例是银行转账。如果在转账过程中系统崩溃，必须保证要么转账成功，要么转账失败，不能出现只扣了一方钱的情况。这就是事务原子性的体现。'
        },
        {
            'case_title': '性能优化案例',
            'case_content': '查询优化前后性能对比',
            'case_speech': '王珊教材中还有一个经典案例：查询优化。同样的查询需求，不同的执行计划性能可能相差几十上百倍。通过代数优化和物理优化，可以大大提升查询效率。'
        },
        {
            'case_title': '安全性案例',
            'case_content': '不同角色用户的权限分配',
            'case_speech': '在安全性章节，教材中通过不同角色用户的权限案例来讲解GRANT和REVOKE的使用。比如教务员可以录入成绩，学生只能查询自己的成绩等。'
        },
        {
            'case_title': '案例：实体完整性的检查',
            'case_content': '向学生表插入主键为空的记录会被拒绝',
            'case_speech': '实体完整性的典型案例：学生表以学号为主键，如果插入一条学号为空的记录，DBMS会直接拒绝该操作，主键列既不能为空也不能重复。'
        },
        {
            'case_title': '案例：参照完整性的违约处理',
            'case_content': '删除被参照的系记录时，RESTRICT拒绝、CASCADE级联删除',
            'case_speech': '参照完整性的典型案例：学生表的系号参照系表。删除系表中某个系时，如果采用RESTRICT策略，因为仍有学生引用该系，操作会被拒绝；如果采用CASCADE策略，相关学生记录会被级联删除。'
        },
    ],
    'sql': [
        {
            'case_title': '教材经典案例：单表查询',
            'case_content': '查询信息系年龄小于20岁的学生',
            'case_speech': '王珊教材中的SQL入门案例：查询信息系所有年龄小于20岁的学生名单。SQL语句是SELECT Sname FROM Student WHERE Sdept=IS AND Sage<20。'
        },
        {
            'case_title': '案例：连接查询',
            'case_content': '查询每个学生及其选修课程的成绩',
            'case_speech': '连接查询的经典案例：查询每个学生的姓名、选修的课程名和成绩。这需要连接学生表、选课表和课程表三张表。'
        },
        {
            'case_title': '案例：嵌套查询',
            'case_content': '查询选修了课程名为数据库的学生姓名',
            'case_speech': '嵌套查询的经典案例：查询选修了课程名为数据库的学生姓名。这个查询可以用嵌套查询实现，先查数据库课程的课程号，再查选修该课的学生学号，最后查学生姓名。'
        },
    ],
    'transaction': [
        {
            'case_title': '教材经典案例：银行转账',
            'case_content': '从账户A转账100元到账户B',
            'case_speech': '王珊教材中事务的经典案例就是银行转账。从账户A转100元到账户B，这个操作包含两个步骤：从A扣钱和给B加钱。这两个步骤必须作为一个整体，要么都做，要么都不做。'
        },
        {
            'case_title': '案例：转账的原子性',
            'case_content': '如果转账过程中系统崩溃怎么办？',
            'case_speech': '假设转账到一半系统崩溃了，会发生什么？如果只扣了A的钱还没加给B，就会出现数据不一致。事务的原子性保证了这种情况不会发生，崩溃后会自动回滚。'
        },
        {
            'case_title': '案例：订票系统并发问题',
            'case_content': '两个人同时买最后一张票',
            'case_speech': '再看火车票订票系统的例子：如果两个人同时查询到只剩最后一张票，然后都下单购买，会发生什么？这就是典型的并发问题，需要通过事务隔离来解决。'
        },
    ],
    'normalization': [
        {
            'case_title': '教材经典案例：学生关系模式',
            'case_content': '学生关系中存在的冗余和异常问题',
            'case_speech': '王珊教材中规范化理论的经典案例：一个包含学号、姓名、系名、系主任、课程名、成绩的关系模式。这个模式存在数据冗余、插入异常、删除异常和修改异常。'
        },
        {
            'case_title': '案例分析：存在的问题',
            'case_content': '数据冗余、插入异常、删除异常、修改异常',
            'case_speech': '这个关系存在四大问题：数据冗余，系主任姓名重复存储；插入异常，新成立的系还没招生就无法插入；删除异常，学生毕业会删掉系的信息；修改异常，更换系主任需要修改多处。'
        },
        {
            'case_title': '案例解决：模式分解',
            'case_content': '分解为学生、系、选课三个关系',
            'case_speech': '通过规范化，我们把这个关系分解为三个关系：学生关系、系关系和选课关系。这样就消除了冗余和各种异常，这就是规范化的意义。'
        },
    ],
}

_CASE_RELEVANCE = {
    '教材中的SQL示例': ['sql', 'select', 'dml', '查询'],
    '教材中的范式示例': ['范式', '规范化', '函数依赖'],
    '教材中的ER模型示例': ['er', 'e-r', '实体联系', '实体-联系', '概念模型'],
    '教材中的恢复技术示例': ['恢复', '日志', '故障'],
    '性能优化案例': ['优化', '查询处理'],
    '安全性案例': ['安全', 'grant', 'revoke'],
    '案例：实体完整性的检查': ['完整性'],
    '案例：参照完整性的违约处理': ['完整性'],
}


def _case_matches(lower_content, case):
    """案例只在主题相符时才会被使用，避免完整性视频里混入ER模型案例。"""
    required = _CASE_RELEVANCE.get(case.get('case_title', ''))
    if not required:
        return True
    return any(kw in lower_content for kw in required)


def _get_case_library(lower_content):
    """根据知识点类型获取对应的案例库"""
    if any(kw in lower_content for kw in ['sql', 'select', '查询', 'ddl', 'dml']):
        library = WANGSHAN_CASES['sql'] + WANGSHAN_CASES['default']
    elif any(kw in lower_content for kw in ['事务', 'acid', '并发', '死锁']):
        library = WANGSHAN_CASES['transaction'] + WANGSHAN_CASES['default']
    elif any(kw in lower_content for kw in ['范式', '规范化', '函数依赖', '数据依赖']):
        library = WANGSHAN_CASES['normalization'] + WANGSHAN_CASES['default']
    else:
        library = WANGSHAN_CASES['default']
    return [case for case in library if _case_matches(lower_content, case)]

def _generate_supplementary_slides(content, category, existing_count, target_count, lower_content):
    """生成补充幻灯片，包含教材案例和扩展内容，确保达到目标页数"""
    cases = _get_case_library(lower_content)
    slides = []
    case_index = 0

    # 扩展模块：教材案例
    if case_index < len(cases) and len(slides) + existing_count < target_count:
        slides.append({
            "slide_number": len(slides) + 1,
            "title": "王珊教材经典案例导入",
            "content": "结合教材中的实际案例加深理解",
            "speech": f"接下来我们结合王珊《数据库系统概论》教材中的经典案例，来深入理解{content}的实际应用。",
            "duration": SECONDS_PER_SLIDE
        })

    while case_index < len(cases) and len(slides) + existing_count < target_count:
        case = cases[case_index]
        slides.append({
            "slide_number": len(slides) + 1,
            "title": case['case_title'],
            "content": case['case_content'],
            "speech": case['case_speech'],
            "duration": SECONDS_PER_SLIDE
        })
        case_index += 1

    # 扩展模块：与其他知识点的联系
    if len(slides) + existing_count < target_count:
        slides.append({
            "slide_number": len(slides) + 1,
            "title": "知识点关联：与其他章节的联系",
            "content": f"{content}在数据库知识体系中的位置",
            "speech": f"我们来看{content}在整个数据库知识体系中的位置。它不是孤立的，而是与其他知识点紧密联系。理解这些联系有助于构建完整的知识体系。",
            "duration": SECONDS_PER_SLIDE
        })

    if len(slides) + existing_count < target_count:
        slides.append({
            "slide_number": len(slides) + 1,
            "title": "考点分析：考试常见题型",
            "content": f"{content}相关的常见考试题型",
            "speech": f"从考试角度来看，{content}相关的题目常见于选择题、简答题和综合题。选择题侧重基本概念，简答题侧重原理阐述，综合题侧重实际应用。",
            "duration": SECONDS_PER_SLIDE
        })

    if len(slides) + existing_count < target_count:
        slides.append({
            "slide_number": len(slides) + 1,
            "title": "易混点辨析：相关概念对比",
            "content": "容易混淆的概念和区别",
            "speech": f"学习{content}时，要注意区分一些容易混淆的概念。只有准确理解每个概念的内涵和外延，才能在实际应用中正确选择和使用。",
            "duration": SECONDS_PER_SLIDE
        })

    if len(slides) + existing_count < target_count:
        slides.append({
            "slide_number": len(slides) + 1,
            "title": "学习方法建议",
            "content": "如何高效学习数据库系统",
            "speech": f"学习{content}的建议：一是理解核心概念，二是结合案例思考，三是动手实践，四是定期复习巩固。理论联系实际是学习数据库最好的方法。",
            "duration": SECONDS_PER_SLIDE
        })

    # 如果还不够，补充通用要点
    extra_topics = [
        ("实际应用中的考量", "在实际项目中选择合适的方案需要考虑多方面因素"),
        ("性能与资源权衡", "数据库设计中经常需要在性能和资源之间做权衡"),
        ("与新技术的结合", "云数据库、分布式数据库等新技术对传统概念的延伸"),
    ]

    for topic_title, topic_content in extra_topics:
        if len(slides) + existing_count >= target_count:
            break
        slides.append({
            "slide_number": len(slides) + 1,
            "title": topic_title,
            "content": topic_content,
            "speech": f"关于{content}的{topic_title}。{topic_content}。理解这些拓展内容，有助于我们在更广阔的视野下理解数据库技术。",
            "duration": SECONDS_PER_SLIDE
        })

    # 最后确保总页数达标
    while len(slides) + existing_count < target_count:
        slides.append({
            "slide_number": len(slides) + 1,
            "title": f"{content} - 扩展要点",
            "content": f"关于{content}的更多深入内容",
            "speech": f"关于{content}，还有很多深入的内容值得探索。建议大家在课后阅读王珊《数据库系统概论》教材的相关章节，进行更系统的学习。",
            "duration": SECONDS_PER_SLIDE
        })

    return slides


def generate_ppt_slides(knowledge_point: KnowledgePoint, question_text: str = "") -> list:
    """根据知识点生成PPT页面内容，严格依据王珊《数据库系统概述》教材"""
    content = knowledge_point.content
    category = knowledge_point.category or '基础概念'
    detail = knowledge_point.detail_content or ''
    key_points = []
    if knowledge_point.key_points:
        try:
            import json
            key_points = json.loads(knowledge_point.key_points) if isinstance(knowledge_point.key_points, str) else knowledge_point.key_points
        except:
            pass

    lower_content = content.lower()

    # 按“具体 → 泛化”的优先级选择PPT模板。
    # 注意：不能用过宽的关键词（如单独的“实体”）判型，否则“实体完整性”会被误判成ER模型。
    if any(kw in lower_content for kw in ['b+树', 'b树', '索引']):
        slides = _generate_btree_slides(content, detail, key_points)
    elif any(kw in lower_content for kw in ['死锁', 'deadlock']):
        slides = _generate_deadlock_slides(content, detail, key_points)
    elif 'acid' in lower_content or '事务' in lower_content:
        slides = _generate_transaction_slides(content, detail, key_points)
    elif 'sql' in lower_content or 'select' in lower_content or 'dml' in lower_content or 'ddl' in lower_content:
        slides = _generate_sql_slides(content, detail, key_points)
    elif '范式' in lower_content or '规范化' in lower_content:
        slides = _generate_normalization_slides(content, detail, key_points)
    elif '完整性' in lower_content:
        slides = _generate_integrity_slides(content, detail, key_points)
    elif '安全性' in lower_content:
        slides = _generate_security_slides(content, detail, key_points)
    elif '恢复' in lower_content or '日志' in lower_content:
        slides = _generate_recovery_slides(content, detail, key_points)
    elif '并发' in lower_content or '锁' in lower_content or 'mvcc' in lower_content:
        slides = _generate_concurrency_slides(content, detail, key_points)
    elif any(kw in lower_content for kw in ['er模型', 'e-r模型', 'e-r', '实体联系', '实体-联系', '概念模型']):
        slides = _generate_er_slides(content, detail, key_points)
    else:
        slides = _generate_general_slides(content, detail, key_points, category)

    # 确保幻灯片数量为目标页数，不足则用教材案例和扩展内容补充
    if len(slides) < SLIDES_COUNT:
        supplementary = _generate_supplementary_slides(
            content, category, len(slides), SLIDES_COUNT, lower_content
        )
        slides.extend(supplementary)
    elif len(slides) > SLIDES_COUNT:
        slides = slides[:SLIDES_COUNT]

    # 重新编号并设置时长
    for i, slide in enumerate(slides):
        slide["slide_number"] = i + 1
        slide["duration"] = SECONDS_PER_SLIDE

    return slides


def _generate_btree_slides(content, detail, key_points):
    return [
        {"slide_number": 1, "title": "B+树索引结构概述", "content": "B+树是数据库中最常用的索引数据结构", "speech": "大家好，今天我们来学习B+树索引结构。B+树是数据库系统中最常用的索引数据结构，它是一种平衡的多路搜索树。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 2, "title": "B+树的基本特征", "content": "所有数据存储在叶子节点，非叶子节点只存索引键", "speech": "B+树的基本特征是：所有实际数据都存储在叶子节点中，非叶子节点只存储索引键用于路由。这种设计使得查找效率非常稳定。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 3, "title": "B+树的结构组成", "content": "根节点、中间节点、叶子节点三层结构", "speech": "B+树由三层组成：根节点位于最顶层，中间节点负责路由指引，叶子节点在最底层存储所有数据记录。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 4, "title": "叶子节点链表", "content": "所有叶子节点通过链表连接，支持范围查询", "speech": "B+树的叶子节点之间通过链表相互连接，这使得范围查询非常高效。只需找到起始位置，沿链表遍历即可。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 5, "title": "教材经典案例：学生表索引", "content": "假设学生表有10000条记录，按学号建立B+树索引", "speech": "我们来看王珊教材中的经典案例：假设有一个学生表，包含10000条学生记录，按照学号建立B+树索引。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 6, "title": "案例分析：树的高度计算", "content": "假设每个节点可存储100个键，树高仅为3层", "speech": "如果每个节点可以存储100个索引键，那么10000条记录的B+树高度仅为3层：根节点100个键，第二层100乘100等于10000个键。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 7, "title": "案例分析：查询效率对比", "content": "顺序查找需5000次IO，B+树仅需3次IO", "speech": "对比一下：如果用顺序查找，平均需要5000次磁盘IO；而用B+树索引，只需要3次IO就能找到记录，效率提升上千倍。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 8, "title": "B+树的插入操作", "content": "插入数据时，节点满则分裂，中间键提升", "speech": "插入数据时，如果叶子节点已满，需要进行节点分裂。分裂后，中间的键值会提升到父节点，保证树的平衡性。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 9, "title": "案例演示：插入过程", "content": "在5阶B+树中依次插入1,2,3,4,5的过程", "speech": "我们来看5阶B+树的插入案例：依次插入1、2、3、4，节点未满正常插入；插入5时节点满，分裂为两个节点，中间键3提升到父节点。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 10, "title": "节点分裂过程详解", "content": "满节点分裂为两个，中间键值提升至父节点", "speech": "节点分裂时，将满节点一分为二，左节点包含前一半键值，右节点包含后一半键值，中间键值提升到父节点。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 11, "title": "B+树的删除操作", "content": "删除数据时，节点过空则合并或借键", "speech": "删除数据时，如果节点中的键值数量少于最小值，需要从兄弟节点借键或者与兄弟节点合并，保持树的平衡。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 12, "title": "案例演示：删除过程", "content": "删除键值后节点元素不足，从左兄弟借键", "speech": "例如删除某个键值后，当前节点只剩1个元素，而最小值为2。这时可以从左兄弟节点借一个键过来，或者与左兄弟合并。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 13, "title": "B+树的查询优势", "content": "查询效率稳定为O(log n)，适合磁盘存储", "speech": "B+树的查询时间复杂度为O(log n)，由于树的高度通常较低，磁盘IO次数少，非常适合数据库的外存存储场景。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 14, "title": "教材案例：图书馆图书检索", "content": "图书馆图书索引系统使用B+树实现快速检索", "speech": "王珊教材中还有图书馆的例子：图书馆的图书检索系统就是用类似B+树的结构，读者按书号检索，能快速定位到书架位置。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 15, "title": "B+树 vs B树", "content": "B+树更适合数据库索引，数据只在叶子节点", "speech": "与B树相比，B+树的数据只存储在叶子节点，非叶子节点能存储更多索引键，树更矮，查询效率更高，是数据库索引的首选。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 16, "title": "B+树 vs 哈希索引", "content": "B+树支持范围查询，哈希索引只支持等值查询", "speech": "与哈希索引相比，B+树不仅支持等值查询，还支持范围查询、排序查询，适用场景更广泛，因此成为数据库默认索引类型。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 17, "title": "聚集索引 vs 非聚集索引", "content": "聚集索引叶子节点存完整数据，非聚集存主键", "speech": "B+树索引分为聚集索引和非聚集索引。聚集索引的叶子节点存储完整数据记录，非聚集索引的叶子节点存储主键值，查询时需要回表。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 18, "title": "实际应用场景", "content": "MySQL InnoDB、Oracle等数据库均使用B+树索引", "speech": "在实际应用中，MySQL的InnoDB存储引擎、Oracle数据库等主流关系数据库，都使用B+树作为默认索引结构，足见其重要性。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 19, "title": "学习要点总结", "content": "结构特征、插入删除、查询优势、实际应用", "speech": "总结一下B+树的学习要点：一是结构特征，二是插入删除操作，三是查询优势，四是在数据库中的实际应用。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 20, "title": "课后思考", "content": "为什么数据库选择B+树而不是红黑树？", "speech": "最后留给大家一个思考题：为什么数据库选择B+树作为索引结构，而不是内存中常用的红黑树呢？关键在于磁盘IO的特性，希望大家课后深入思考。", "duration": SECONDS_PER_SLIDE},
    ]


def _generate_deadlock_slides(content, detail, key_points):
    return [
        {"slide_number": 1, "title": "死锁的概念", "content": "两个或多个事务互相等待对方释放资源", "speech": "今天我们学习数据库中的死锁。死锁是指两个或多个事务在执行过程中，因争夺资源而互相等待的现象。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 2, "title": "死锁的形成条件", "content": "互斥、占有并等待、不可抢占、循环等待", "speech": "死锁的形成需要四个必要条件：资源互斥、事务占有资源并等待新资源、资源不可抢占、事务间形成循环等待链。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 3, "title": "死锁示例", "content": "T1持有L1请求L2，T2持有L2请求L1", "speech": "举个例子：事务T1持有锁L1，同时请求锁L2；事务T2持有锁L2，同时请求锁L1。两个事务都无法继续，形成死锁。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 4, "title": "教材经典案例：银行转账死锁", "content": "两个账户互相转账时可能发生死锁", "speech": "王珊教材中的经典案例：银行转账。事务1从账户A向账户B转账，事务2从账户B向账户A转账，如果加锁顺序不同，就会发生死锁。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 5, "title": "案例分析：银行转账场景", "content": "T1:A→B, T2:B→A，按相反顺序加锁", "speech": "具体来说，事务1先锁定账户A再锁定账户B，事务2先锁定账户B再锁定账户A，这样就形成了循环等待，导致死锁。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 6, "title": "案例解决方案：统一加锁顺序", "content": "所有事务都按账户号从小到大的顺序加锁", "speech": "解决方法是统一加锁顺序：规定所有转账事务都按照账户号从小到大的顺序加锁，这样就不会形成循环等待，从而预防死锁。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 7, "title": "死锁的检测", "content": "等待图检测法，图中存在环则发生死锁", "speech": "数据库系统通过等待图来检测死锁。如果等待图中存在环路，说明发生了死锁，系统会选择一个事务作为牺牲者进行回滚。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 8, "title": "死锁的预防：一次封锁法", "content": "事务一次性申请所有需要的资源", "speech": "死锁预防的第一种方法是一次封锁法：要求事务在执行前一次性申请所有需要的资源，如果有一个资源申请失败，则不占有任何资源。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 9, "title": "死锁的预防：顺序封锁法", "content": "所有事务按固定顺序申请资源", "speech": "第二种方法是顺序封锁法：预先对所有资源规定一个封锁顺序，所有事务都按照这个顺序申请资源，从而避免循环等待。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 10, "title": "教材案例：商品库存系统", "content": "商品和库存记录的加锁顺序问题", "speech": "再看教材中的另一个案例：商品销售系统。如果事务1先锁商品再锁库存，事务2先锁库存再锁商品，就会发生死锁。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 11, "title": "案例分析：顺序封锁的应用", "content": "规定先锁商品表，再锁库存表", "speech": "解决方法是规定统一顺序：所有事务都先锁定商品表，再锁定库存表。这样破坏了循环等待条件，死锁就不会发生了。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 12, "title": "死锁的解除：选择牺牲者", "content": "根据代价选择回滚哪个事务", "speech": "检测到死锁后，需要选择一个事务作为牺牲者进行回滚。选择依据通常包括：事务的优先级、已执行时间、持有资源数量等。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 13, "title": "死锁的解除：回滚策略", "content": "完全回滚或部分回滚", "speech": "回滚策略有两种：完全回滚，将事务全部撤销；部分回滚，只回滚到能解除死锁的程度。部分回滚效率更高但实现更复杂。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 14, "title": "超时机制", "content": "设置等待超时时间，超时自动回滚", "speech": "数据库还可以采用超时机制，如果事务等待锁的时间超过设定阈值，系统自动将该事务回滚，避免长时间死锁。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 15, "title": "死锁与活锁的区别", "content": "死锁是永久等待，活锁是可能等待很久", "speech": "注意区分死锁和活锁：死锁是两个事务都永久等待；活锁是事务可能等待很长时间，但理论上最终可能获得资源。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 16, "title": "Oracle中的死锁处理", "content": "Oracle自动检测死锁，回滚代价小的事务", "speech": "在Oracle数据库中，系统会自动检测死锁，当检测到死锁时，会回滚那个代价较小的语句或事务，并返回错误提示。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 17, "title": "MySQL中的死锁处理", "content": "InnoDB采用等待图检测死锁", "speech": "MySQL的InnoDB引擎也采用等待图方式检测死锁，检测到死锁后回滚持有最少行级排他锁的事务。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 18, "title": "死锁频率的估算", "content": "死锁概率与事务数量、数据项数量正相关", "speech": "死锁发生的概率与系统中事务的数量、每个事务访问的数据项数量、事务的长度等因素正相关。系统越繁忙，死锁概率越高。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 19, "title": "学习要点总结", "content": "形成条件、预防方法、检测解除、实际应用", "speech": "总结一下死锁的学习要点：四个形成条件、两种预防方法、检测与解除机制、以及在实际数据库系统中的应用。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 20, "title": "课后思考", "content": "在实际开发中如何避免死锁？", "speech": "课后思考题：在你的项目开发中，有哪些编程实践可以预防死锁的发生？请从加锁顺序、事务粒度、超时设置等方面思考。", "duration": SECONDS_PER_SLIDE},
    ]


def _generate_transaction_slides(content, detail, key_points):
    return [
        {"slide_number": 1, "title": "事务的基本概念", "content": "事务是数据库操作的最小逻辑工作单位", "speech": "今天我们学习数据库事务。事务是用户定义的一个数据库操作序列，这些操作要么全部执行，要么全部不执行。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 2, "title": "事务的ACID特性", "content": "原子性、一致性、隔离性、持久性", "speech": "事务具有ACID四大特性：原子性、一致性、隔离性和持久性。这是保证数据库正确性的基石。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 3, "title": "原子性 Atomicity", "content": "事务中的操作要么全做，要么全不做", "speech": "原子性要求事务中的所有操作要么全部执行，要么全部不执行。如果事务执行失败，已执行的操作必须回滚。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 4, "title": "一致性 Consistency", "content": "事务执行前后，数据库保持一致状态", "speech": "一致性要求事务执行前后，数据库从一个一致状态转变到另一个一致状态，不会破坏完整性约束。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 5, "title": "隔离性 Isolation", "content": "并发执行的事务之间互不干扰", "speech": "隔离性要求多个事务并发执行时，一个事务的执行不应影响其他事务的执行，各事务之间相互隔离。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 6, "title": "持久性 Durability", "content": "事务提交后，修改永久保存", "speech": "持久性保证事务一旦提交，其对数据库的修改就是永久的，即使系统故障也不会丢失。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 7, "title": "事务的状态转换", "content": "活动→部分提交→提交/失败→中止/结束", "speech": "事务经历活动状态、部分提交状态、提交状态或失败状态、中止状态，最终完成或回滚结束。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 8, "title": "总结", "content": "ACID特性保证数据库的可靠性和正确性", "speech": "总结一下，ACID特性是数据库事务的核心，它们共同保证了数据库系统在并发访问和故障情况下的可靠性和正确性。", "duration": SECONDS_PER_SLIDE},
    ]


def _generate_sql_slides(content, detail, key_points):
    return [
        {"slide_number": 1, "title": "SQL语言概述", "content": "结构化查询语言，关系数据库的标准语言", "speech": "今天我们学习SQL语言。SQL是结构化查询语言，是关系数据库的标准语言，用于定义、操纵、查询和控制数据。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 2, "title": "SQL语言分类", "content": "DDL、DML、DQL、DCL四大类型", "speech": "SQL语言分为四类：数据定义语言DDL、数据操纵语言DML、数据查询语言DQL和数据控制语言DCL。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 3, "title": "数据定义语言DDL", "content": "CREATE、ALTER、DROP语句", "speech": "DDL用于定义数据库结构，包括CREATE创建表、ALTER修改表结构、DROP删除表等操作。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 4, "title": "数据操纵语言DML", "content": "INSERT、UPDATE、DELETE语句", "speech": "DML用于操纵数据，包括INSERT插入数据、UPDATE更新数据、DELETE删除数据三种基本操作。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 5, "title": "数据查询语言DQL", "content": "SELECT语句，最常用的SQL语句", "speech": "DQL的核心是SELECT语句，用于从数据库中查询数据。支持WHERE条件过滤、GROUP BY分组、ORDER BY排序等功能。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 6, "title": "SELECT语句详解", "content": "SELECT...FROM...WHERE...GROUP BY...HAVING...ORDER BY", "speech": "SELECT语句的完整语法包括SELECT指定列、FROM指定表、WHERE设置条件、GROUP BY分组、HAVING过滤分组、ORDER BY排序。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 7, "title": "数据控制语言DCL", "content": "GRANT授权、REVOKE收回权限", "speech": "DCL用于控制数据库访问权限，GRANT语句授予权限，REVOKE语句收回权限，保证数据库的安全性。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 8, "title": "总结", "content": "SQL是数据库操作的核心语言，掌握SQL至关重要", "speech": "总结一下，SQL语言是数据库操作的核心，掌握DDL、DML、DQL、DCL四类语句，是学习数据库系统的基础和关键。", "duration": SECONDS_PER_SLIDE},
    ]


def _generate_normalization_slides(content, detail, key_points):
    return [
        {"slide_number": 1, "title": "规范化理论概述", "content": "消除数据冗余，提高数据一致性", "speech": "今天我们学习数据库规范化理论。规范化的目的是消除关系模式中的数据冗余和更新异常，提高数据一致性。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 2, "title": "函数依赖", "content": "属性间的依赖关系，是规范化的基础", "speech": "函数依赖是规范化的基础。如果属性X的值能唯一确定属性Y的值，则称Y函数依赖于X，记作X→Y。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 3, "title": "第一范式1NF", "content": "每个属性不可再分，满足原子性", "speech": "第一范式要求关系中的每个属性都是不可再分的原子值，这是关系模式最基本的要求。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 4, "title": "第二范式2NF", "content": "消除非主属性对码的部分函数依赖", "speech": "第二范式在1NF基础上，要求消除非主属性对候选码的部分函数依赖，确保每个非主属性完全依赖于码。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 5, "title": "第三范式3NF", "content": "消除非主属性对码的传递函数依赖", "speech": "第三范式在2NF基础上，要求消除非主属性对候选码的传递函数依赖，进一步减少数据冗余。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 6, "title": "BCNF范式", "content": "消除主属性对码的部分和传递依赖", "speech": "BCNF范式在3NF基础上，要求消除主属性对候选码的部分函数依赖和传递函数依赖，是比3NF更严格的范式。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 7, "title": "模式分解", "content": "将低范式关系分解为高范式关系", "speech": "模式分解是提高范式级别的方法，将一个低范式的关系模式分解为多个高范式的关系模式，要求保持函数依赖和无损连接。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 8, "title": "总结", "content": "规范化是数据库设计的重要理论", "speech": "总结一下，规范化理论是数据库设计的理论基础，通过逐步消除不合适的函数依赖，设计出结构合理的关系模式。", "duration": SECONDS_PER_SLIDE},
    ]


def _generate_er_slides(content, detail, key_points):
    return [
        {"slide_number": 1, "title": "ER模型概述", "content": "实体-联系模型，用于概念设计", "speech": "今天我们学习ER模型。ER模型即实体-联系模型，是数据库概念设计阶段最常用的建模工具。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 2, "title": "实体 Entity", "content": "客观存在并可相互区别的事物", "speech": "实体是客观存在并可相互区别的事物，如学生、课程、教师等。实体用矩形表示，具有一组属性。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 3, "title": "属性 Attribute", "content": "实体所具有的某一特性", "speech": "属性是实体所具有的特性，如学生的学号、姓名、年龄等。属性用椭圆形表示，分为简单属性和复合属性。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 4, "title": "联系 Relationship", "content": "实体之间的关联，用菱形表示", "speech": "联系是实体之间的关联关系，用菱形表示。联系也可以有属性，如学生选课联系中的成绩属性。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 5, "title": "联系的类型", "content": "一对一、一对多、多对多", "speech": "联系有三种类型：一对一联系如部门与经理、一对多联系如班级与学生、多对多联系如学生与课程。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 6, "title": "ER图的设计步骤", "content": "识别实体→确定属性→定义联系→标注基数", "speech": "ER图的设计步骤：首先识别实体，然后确定各实体的属性，接着定义实体间的联系，最后标注联系的基数。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 7, "title": "ER模型转关系模式", "content": "实体转关系，联系根据基数处理", "speech": "ER模型转换为关系模式时，实体转换为关系，一对一联系可并入任一实体，一对多联系并入多端实体，多对多联系需单独建表。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 8, "title": "总结", "content": "ER模型是数据库概念设计的核心工具", "speech": "总结一下，ER模型通过实体、属性和联系描述现实世界，是数据库概念设计阶段最重要的建模工具。", "duration": SECONDS_PER_SLIDE},
    ]


def _generate_recovery_slides(content, detail, key_points):
    return [
        {"slide_number": 1, "title": "数据库恢复概述", "content": "保证事务的原子性和持久性", "speech": "今天我们学习数据库恢复技术。数据库恢复的目的是在系统发生故障后，保证事务的原子性和持久性。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 2, "title": "故障分类", "content": "事务故障、系统故障、介质故障", "speech": "数据库故障分为三类：事务故障是事务内部错误，系统故障是系统停止运行，介质故障是磁盘等存储介质损坏。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 3, "title": "日志文件", "content": "记录事务对数据库的所有修改", "speech": "日志文件记录事务对数据库的所有修改操作，是恢复的基础。日志必须先写，数据后写，保证可恢复性。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 4, "title": "UNDO和REDO", "content": "撤销未完成事务，重做已提交事务", "speech": "恢复的核心操作是UNDO和REDO：UNDO撤销未完成事务的修改，REDO重做已提交但未写入磁盘的事务。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 5, "title": "检查点技术", "content": "定期保存系统状态，减少恢复工作量", "speech": "检查点技术定期将日志缓冲区写入磁盘，并记录系统状态。恢复时只需处理检查点之后的事务，大大减少恢复时间。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 6, "title": "事务故障恢复", "content": "反向扫描日志，UNDO未完成事务", "speech": "事务故障恢复：反向扫描日志，对未完成的事务执行UNDO操作，撤销其对数据库的所有修改。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 7, "title": "系统故障恢复", "content": "正向REDO已提交事务，反向UNDO未完成事务", "speech": "系统故障恢复：正向扫描日志重做已提交事务，反向扫描日志撤销未完成事务，保证数据库恢复到一致状态。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 8, "title": "总结", "content": "恢复技术保证数据库的可靠性和数据安全", "speech": "总结一下，数据库恢复技术通过日志、检查点和UNDO/REDO机制，保证数据库在故障后能恢复到一致状态。", "duration": SECONDS_PER_SLIDE},
    ]


def _generate_concurrency_slides(content, detail, key_points):
    return [
        {"slide_number": 1, "title": "并发控制概述", "content": "保证多事务并发执行的正确性", "speech": "今天我们学习并发控制。并发控制的目的是保证多个事务并发执行时，数据库的一致性不被破坏。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 2, "title": "并发问题", "content": "丢失修改、脏读、不可重复读、幻读", "speech": "并发执行可能导致四种问题：丢失修改、脏读、不可重复读和幻读，这些都会影响数据的一致性。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 3, "title": "封锁机制", "content": "共享锁S锁和排他锁X锁", "speech": "封锁是并发控制的基本方法。共享锁S锁允许多事务读，排他锁X锁只允许一个事务读写，两者互斥。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 4, "title": "封锁协议", "content": "一级、二级、三级封锁协议", "speech": "封锁协议分为三级：一级协议防丢失修改，二级协议防脏读，三级协议防不可重复读，级别越高隔离性越强。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 5, "title": "两段锁协议", "content": "扩展阶段加锁，收缩阶段解锁", "speech": "两段锁协议将事务分为扩展和收缩两阶段：扩展阶段只能加锁，收缩阶段只能解锁，可保证可串行化。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 6, "title": "事务隔离级别", "content": "读未提交、读已提交、可重复读、串行化", "speech": "SQL标准定义四种隔离级别：读未提交、读已提交、可重复读和串行化，隔离级别越高，并发性能越低。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 7, "title": "MVCC多版本并发控制", "content": "通过版本链实现读写不互相阻塞", "speech": "MVCC通过维护数据的多个版本，使读操作不阻塞写操作，写操作也不阻塞读操作，大大提高了并发性能。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 8, "title": "总结", "content": "并发控制保证数据库在多用户环境下的正确性", "speech": "总结一下，并发控制通过封锁协议、隔离级别和MVCC等机制，保证数据库在多用户并发访问时的数据一致性。", "duration": SECONDS_PER_SLIDE},
    ]


def _generate_integrity_slides(content, detail, key_points):
    return [
        {"slide_number": 1, "title": "数据库完整性概述", "content": "保证数据的正确性和相容性", "speech": "今天我们学习数据库完整性。完整性约束保证数据库中的数据是正确的、有效的和相容的。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 2, "title": "实体完整性", "content": "主键非空且唯一", "speech": "实体完整性要求主键属性既不能为空也不能重复，每个实体必须有唯一的标识。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 3, "title": "参照完整性", "content": "外键必须为空或等于被参照关系的主键", "speech": "参照完整性要求外键值要么为空，要么必须等于被参照关系中某个主键的值，保证表间引用的正确性。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 4, "title": "用户定义完整性", "content": "根据应用需求定义的约束条件", "speech": "用户定义完整性是根据具体应用需求定义的约束，如年龄必须在0到150之间，成绩不能为负数等。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 5, "title": "完整性约束的定义", "content": "列级约束和表级约束", "speech": "完整性约束可以在列定义时定义列级约束，也可以在表定义时定义表级约束，如CHECK、UNIQUE、DEFAULT等。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 6, "title": "触发器", "content": "自动执行的完整性检查机制", "speech": "触发器是一种特殊的存储过程，在对表进行INSERT、UPDATE、DELETE操作时自动执行，用于实现复杂的完整性约束。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 7, "title": "违约处理", "content": "RESTRICT拒绝、CASCADE级联、SET NULL置空", "speech": "当违反完整性约束时，系统可以采取RESTRICT拒绝操作、CASCADE级联操作或SET NULL置空等方式处理。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 8, "title": "总结", "content": "完整性约束是数据库正确性的重要保障", "speech": "总结一下，数据库完整性通过实体完整性、参照完整性和用户定义完整性三层约束，保证数据的正确性和一致性。", "duration": SECONDS_PER_SLIDE},
    ]


def _generate_security_slides(content, detail, key_points):
    return [
        {"slide_number": 1, "title": "数据库安全性概述", "content": "保护数据库防止非法访问和破坏", "speech": "今天我们学习数据库安全性。数据库安全性的目标是保护数据库，防止未经授权的访问、修改和破坏。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 2, "title": "用户标识与鉴别", "content": "系统核对用户身份，最外层安全", "speech": "用户标识与鉴别是数据库安全的第一道防线，系统通过用户名和密码等方式核对用户身份，确保合法用户才能访问。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 3, "title": "自主存取控制DAC", "content": "用户自主管理数据访问权限", "speech": "自主存取控制允许用户将自己拥有的权限授予他人，通过GRANT授权和REVOKE收回权限实现灵活的权限管理。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 4, "title": "强制存取控制MAC", "content": "系统根据安全级别强制控制访问", "speech": "强制存取控制为每个数据和用户分配安全级别，系统强制执行访问控制规则，安全性比DAC更高。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 5, "title": "视图机制", "content": "通过视图限制用户可见数据范围", "speech": "视图机制通过定义视图，限制用户只能看到与自己相关的数据，隐藏敏感信息，是一种重要的安全保护措施。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 6, "title": "审计", "content": "记录用户操作日志，追踪非法访问", "speech": "审计功能记录用户对数据库的所有操作，形成审计日志，用于追踪非法访问和安全事件，是事后追责的依据。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 7, "title": "数据加密", "content": "对存储和传输的数据进行加密", "speech": "数据加密通过对存储和传输的数据进行加密处理，即使数据被窃取也无法读取内容，是最高级别的安全措施。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 8, "title": "总结", "content": "多层次安全防护保证数据库安全", "speech": "总结一下，数据库安全通过标识鉴别、存取控制、视图、审计和加密等多层次防护，全方位保护数据库安全。", "duration": SECONDS_PER_SLIDE},
    ]


def _generate_general_slides(content, detail, key_points, category):
    """通用的知识点PPT生成"""
    kp_text = "、".join(key_points[:3]) if key_points else "核心概念和要点"
    return [
        {"slide_number": 1, "title": f"{content}概述", "content": f"{category}类知识点", "speech": f"大家好，今天我们来学习{content}。这是数据库系统中{category}类的重要知识点。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 2, "title": "基本概念", "content": content, "speech": f"首先，{content}是数据库系统中的一个基本概念。{detail[:50] if detail else '它涉及数据库系统的核心原理。'}", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 3, "title": "核心要点", "content": kp_text, "speech": f"{content}的核心要点包括：{kp_text}。这些要点是理解和掌握该知识点的关键。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 4, "title": "详细说明", "content": "知识点的详细内容", "speech": f"下面详细讲解{content}的具体内容。它涉及多个方面，需要从不同角度理解其内涵和外延。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 5, "title": "关键特性", "content": "主要特点和性质", "speech": f"{content}具有一些重要的特性。了解这些特性有助于我们更好地运用这一概念解决实际问题。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 6, "title": "应用场景", "content": "在实际数据库系统中的应用", "speech": f"{content}在实际数据库系统中有广泛的应用场景，掌握它对于数据库系统的设计和实现非常重要。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 7, "title": "注意事项", "content": "学习要点和易错点", "speech": f"学习{content}时需要注意一些关键点和容易混淆的地方，避免在实际应用中出现错误。", "duration": SECONDS_PER_SLIDE},
        {"slide_number": 8, "title": "总结", "content": "知识点总结回顾", "speech": f"总结一下，{content}是数据库系统中的重要知识点，通过今天的学习，希望大家能够深入理解并灵活运用。", "duration": SECONDS_PER_SLIDE},
    ]


# ==================== 聚焦小知识点的视频生成 ====================
# 当提问只针对知识点内部的某个小节（例如“演示delete语句”）时，
# 只围绕该小节生成视频，避免把整个知识点（含 INSERT/UPDATE/DELETE）都讲一遍。

_STATEMENT_FOCUS = [
    ("delete", "DELETE", ["delete", "删除"]),
    ("insert", "INSERT", ["insert", "插入"]),
    ("update", "UPDATE", ["update", "更新"]),
    ("select", "SELECT", ["select", "查询", "检索"]),
]


def _detect_statement(text: str):
    """从文本中识别用户聚焦的是哪一条 SQL 语句；识别不到返回 None。"""
    lower = (text or "").lower()
    for key, _short, keywords in _STATEMENT_FOCUS:
        for kw in keywords:
            if kw in lower:
                return key
    return None


# 仅英文的语句名，作为“用户明确点名某条 SQL 语句”的强信号
_ENGLISH_STATEMENT_KEYWORDS = [
    ("delete", "delete"),
    ("insert", "insert"),
    ("update", "update"),
    ("select", "select"),
]


def _detect_statement_english(text: str):
    lower = (text or "").lower()
    for key, kw in _ENGLISH_STATEMENT_KEYWORDS:
        if kw in lower:
            return key
    return None


# 每条语句的独立视频内容（严格只讲解该语句本身，20 页 PPT / 300 秒）
_STATEMENT_VIDEO = {
    "delete": {
        "short": "DELETE",
        "name": "DELETE 语句：删除数据",
        "concept": (
            "DELETE 用于从表中删除满足条件的数据行，属于 DML 中负责删除的语句。",
            "本节视频只讲解 DELETE 语句。DELETE 是数据操纵语言 DML 中负责删除数据的语句，用来删除表中满足条件的行，下面所有内容都只围绕 DELETE 展开。",
        ),
        "purpose": (
            "删除表中不再需要的行，表结构保持不变。",
            "DELETE 的作用是删除表中不再需要的记录，它只删除数据行，不删除表本身，表结构和索引依然保留。",
        ),
        "syntax": (
            "DELETE FROM <表名> [WHERE <条件>];",
            "DELETE 的基本语法是：DELETE FROM 表名，后面可以跟 WHERE 条件。这条语句的含义是从指定表中删除符合条件的行。",
        ),
        "clauses": (
            "FROM 指定目标表；WHERE 指定删除条件，省略则删除全部行。",
            "语句由两部分组成：FROM 指定要操作的目标表，WHERE 指定删除条件。这里要特别注意，WHERE 是可以省略的，但省略后整张表的所有行都会被删除。",
        ),
        "steps": [
            ("执行流程①：定位目标行", "按 WHERE 条件扫描并找出要删除的行", "执行 DELETE 时，数据库首先根据 WHERE 条件扫描表，定位出所有满足条件的行。"),
            ("执行流程②：加锁并删除", "对目标行加排他锁后逐行删除", "定位到目标行后，系统会对这些行加排他锁，然后逐行把它们从表中删除。"),
            ("执行流程③：写日志并提交", "删除写入日志，提交后生效且可回滚", "删除操作会记入日志，事务提交后才永久生效；在提交之前，如果发现有误，还可以回滚撤销。"),
        ],
        "case_scene": (
            "学生表 Student(Sno,Sname,Sage)，需要删除学号为 2024009 的这名学生。",
            "我们来看教材中的例子：学生表 Student 包含学号、姓名、年龄等字段，现在需要删除学号为 2024009 的学生记录。",
        ),
        "case_sql": (
            "DELETE FROM Student WHERE Sno = '2024009';",
            "对应的 SQL 语句是：DELETE FROM Student WHERE Sno 等于 2024009。这里只删除了学号为 2024009 的这一行。",
        ),
        "case_result": (
            "只删除 Sno=2024009 的那一行；若省略 WHERE，则整表数据被清空。",
            "执行后只删除了学号为 2024009 的一行记录。如果这条语句漏写了 WHERE，那么 Student 表里的所有行都会被删除，这是非常危险的。",
        ),
        "notes": [
            ("注意事项①：WHERE 是安全阀", "删除前务必用相同条件的查询先核对命中范围", "使用 DELETE 时一定要谨慎书写 WHERE 条件，建议先用相同条件的查询确认将要删除的记录，再执行删除。"),
            ("注意事项②：DELETE 与 DROP 不同", "DELETE 只删数据保留表结构，DROP 删除整张表", "还要区分 DELETE 和 DROP：DELETE 只删除表中的数据行，表结构依然存在；而 DROP 会把整张表连结构一起删除。"),
        ],
        "errors": [
            ("常见错误①：漏写 WHERE 导致全表被删", "这是最常见的误操作", "最常见的错误是漏写 WHERE 条件，结果把整张表的数据全部删光，实践中务必确认条件后再执行。"),
            ("常见错误②：外键约束导致删除失败", "被引用的行可能被拒绝删除或触发级联删除", "如果被删除的行被其他表的外键引用，删除可能被拒绝；如果设置了级联规则，还会连带删除相关联的数据，需要格外注意。"),
        ],
        "compare": (
            "DELETE 可带条件、逐行删除、可回滚；TRUNCATE 快速清空全表且一般不可回滚；DROP 删除表结构。",
            "把 DELETE 和另外两条语句对比：DELETE 可以带条件、逐行删除并且可以回滚；TRUNCATE 用来快速清空全表，但一般不可回滚还会重置自增计数；DROP 则是直接删除整张表。",
        ),
        "transaction": (
            "DELETE 属于 DML，受事务控制，未提交前可用 ROLLBACK 撤销。",
            "DELETE 属于 DML 语句，受事务控制。把删除操作放在事务中，确认无误后再提交，一旦发现异常可以立即回滚。",
        ),
        "perf": (
            "大批量删除建议分批提交，WHERE 条件列建立索引以避免全表扫描。",
            "性能方面，大批量删除建议分批提交，避免长时间锁定；同时给 WHERE 条件列建立索引，可以减少扫描范围、提升删除效率。",
        ),
        "review": (
            "定位目标行 → 加锁删除 → 写日志并提交。",
            "回顾一下 DELETE 的执行过程：先按条件定位目标行，再加锁逐行删除，最后写入日志并在提交后生效。",
        ),
        "summary": (
            "DELETE 删除满足条件的行、保留表结构；WHERE 是安全阀，不能漏写；受事务控制、可回滚；与 DROP、TRUNCATE 语义不同。",
            "总结本节要点：DELETE 只删除满足条件的行、保留表结构；WHERE 是关键的安全条件，不能漏写；它受事务控制、可以回滚；并且要与 DROP、TRUNCATE 区分开。",
        ),
        "question": (
            "如果要删除学生表中的全部数据但保留表结构，应该使用哪条语句？",
            "留一个思考题：如果要删除学生表中的全部数据，同时还要保留表结构，应该使用哪条语句呢？请结合本节内容想一想。",
        ),
    },
    "insert": {
        "short": "INSERT",
        "name": "INSERT 语句：插入数据",
        "concept": (
            "INSERT 用于向表中插入新的数据行，是 DML 中负责新增数据的语句。",
            "本节视频只讲解 INSERT 语句。INSERT 是数据操纵语言 DML 中负责插入数据的语句，用来向表中新增数据行，下面只围绕 INSERT 展开。",
        ),
        "purpose": (
            "向指定表写入一行或多行新数据，也可写入子查询结果。",
            "INSERT 的作用是向表中写入新的数据，既可以插入单行、多行，也可以把一条查询结果批量写入目标表。",
        ),
        "syntax": (
            "INSERT INTO <表名> (<列名>...) VALUES (<值>...);",
            "INSERT 的基本语法是：INSERT INTO 表名，括号里列出列名，VALUES 后面给出对应的值。列与值必须一一对应。",
        ),
        "clauses": (
            "INTO 指定目标表；列名列表指定要写入的列；VALUES 给出与列一一对应的值。",
            "语句由三部分组成：INTO 指定目标表，列名列表指定要写入哪些列，VALUES 给出与列一一对应的值。省略列名列表时要按表中全部列的默认顺序提供值。",
        ),
        "steps": [
            ("执行流程①：确定目标表与列", "选择要写入的表和对应列", "插入时首先要确定目标表和要写入的列，列的顺序可以和建表时不同，但必须与值的顺序一一对应。"),
            ("执行流程②：校验数据", "检查数据类型、非空、主码和外码约束", "接着系统会校验数据：值的数据类型要与列匹配，非空列不能省略，主码不能重复，有外码约束时值必须存在于被引用表中。"),
            ("执行流程③：写入并提交", "写入数据并记入日志，提交后生效", "校验通过后数据被写入表中并记入日志，事务提交后插入才永久生效。"),
        ],
        "case_scene": (
            "图书馆管理系统采购完成后，管理员需要逐批录入新书信息。",
            "我们看教材中图书馆管理系统的例子：采购完成后，管理员要把新书信息逐批录入图书表。",
        ),
        "case_sql": (
            "INSERT INTO 图书(书号,书名,作者,状态) VALUES ('TP311','数据库系统概论','王珊','在架');",
            "对应的 SQL 是：INSERT INTO 图书，指定书号、书名、作者、状态四列，VALUES 给出对应的值，这样就插入了一条新书记录。",
        ),
        "case_result": (
            "在图书表中新增一行，其余记录不受影响。",
            "执行后图书表中新增了一行新书记录，其他记录不受任何影响，这正是 INSERT 只负责新增数据的体现。",
        ),
        "notes": [
            ("注意事项①：列与值一一对应", "列的顺序可不同，但值必须按列的排列顺序给出", "使用 INSERT 时要注意列与值必须一一对应，列的顺序可以不同于建表顺序，但值的顺序必须与列一致。"),
            ("注意事项②：批量插入效率更高", "VALUES 后可写多组括号，一次插入多行", "如果需要插入多条数据，可以在 VALUES 后一次写多组括号，用逗号分隔，这样比逐条插入效率更高。"),
        ],
        "errors": [
            ("常见错误①：数据类型或数量不匹配", "值与列的数量、类型必须一致", "常见错误是提供的值与列数量不一致或类型不匹配，系统会直接报错拒绝插入。"),
            ("常见错误②：违反完整性约束", "主码重复或外码不存在导致插入失败", "如果主码重复，或者外码值在被引用表中不存在，插入会因为违反完整性约束而失败。"),
        ],
        "compare": (
            "INSERT 负责新增；UPDATE 负责修改；DELETE 负责删除，三者共同构成 DML 的数据维护操作。",
            "把 INSERT 和另外两条语句对比：INSERT 负责新增数据，UPDATE 负责修改数据，DELETE 负责删除数据，三者共同构成 DML 的数据维护操作。",
        ),
        "transaction": (
            "INSERT 属于 DML，受事务控制，批量插入应放在事务中确认后再提交。",
            "INSERT 同样受事务控制，批量插入建议放在一个事务里，确认无误后再提交，必要时可以回滚。",
        ),
        "perf": (
            "批量插入优于逐条插入，插入时注意索引和约束的校验开销。",
            "性能方面，批量插入比逐条插入高效得多；同时要注意索引和外键约束在插入时都会带来额外的校验开销。",
        ),
        "review": (
            "确定表与列 → 校验数据 → 写入并提交。",
            "回顾 INSERT 的执行过程：先确定目标表与列，再校验数据类型和约束，最后写入数据并在提交后生效。",
        ),
        "summary": (
            "INSERT 向表中插入新数据行；列与值必须一一对应；支持单行、多行和子查询结果插入；受完整性约束与事务控制。",
            "总结本节要点：INSERT 用于插入新的数据行；列与值必须一一对应；支持单行、多行和子查询结果插入；并且受完整性约束和事务控制。",
        ),
        "question": (
            "要一次性把查询结果批量写入一张汇总表，应该使用哪种 INSERT 形式？",
            "课后思考题：如果要把一条查询的结果一次性批量写入汇总表，应该使用哪种 INSERT 形式呢？",
        ),
    },
    "update": {
        "short": "UPDATE",
        "name": "UPDATE 语句：更新数据",
        "concept": (
            "UPDATE 用于修改表中已有数据行的列值，是 DML 中负责更新的语句。",
            "本节视频只讲解 UPDATE 语句。UPDATE 是数据操纵语言 DML 中负责修改数据的语句，用来更新表中已有行的列值，下面只围绕 UPDATE 展开。",
        ),
        "purpose": (
            "修改已有记录的指定列，可同时更新多列。",
            "UPDATE 的作用是修改表中已有记录，可以一次更新一列，也可以同时更新多列。",
        ),
        "syntax": (
            "UPDATE <表名> SET <列名>=<表达式> [,...] [WHERE <条件>];",
            "UPDATE 的语法是：UPDATE 表名 SET 列等于表达式，可以写多组用逗号分隔，后面跟 WHERE 条件。",
        ),
        "clauses": (
            "SET 指定要修改的列和新值；WHERE 指定要更新的记录，省略则更新全部行。",
            "语句由 SET 和 WHERE 两部分组成：SET 指定要修改的列和新值，WHERE 指定要更新的记录。省略 WHERE 时表中所有行都会被更新。",
        ),
        "steps": [
            ("执行流程①：定位目标行", "按 WHERE 条件找出要更新的行", "执行 UPDATE 时，系统先根据 WHERE 条件定位出需要更新的行。"),
            ("执行流程②：加锁并计算新值", "对目标行加锁，按 SET 表达式计算新值", "随后对目标行加锁，根据 SET 子句中的表达式计算每一列的新值。"),
            ("执行流程③：更新并提交", "写入新值并记入日志，提交后生效", "新值被写回并记入日志，事务提交后更新才永久生效。"),
        ],
        "case_scene": (
            "公司为销售部员工统一上调工资 10%。",
            "来看一个例子：公司决定给销售部员工统一上调工资百分之十。",
        ),
        "case_sql": (
            "UPDATE 员工 SET 工资=工资*1.1 WHERE 部门='销售部';",
            "对应的 SQL 是：UPDATE 员工 SET 工资等于工资乘以一点一，WHERE 部门等于销售部。这样只更新销售部员工的工资。",
        ),
        "case_result": (
            "只更新销售部员工的工资，其他部门不受影响。",
            "执行后只有销售部员工的工资被更新，其他部门的记录保持不变，这得益于 WHERE 条件限定了范围。",
        ),
        "notes": [
            ("注意事项①：WHERE 决定影响范围", "省略 WHERE 会更新全表所有行，属于高危操作", "使用 UPDATE 时 WHERE 决定了影响范围，省略 WHERE 会把表中所有行都更新一遍，属于高危操作。"),
            ("注意事项②：可用表达式做批量计算", "如 工资=工资*1.1 实现统一调薪", "SET 中可以使用表达式，比如工资等于工资乘以一点一，可以方便地实现整批数据的统一调整。"),
        ],
        "errors": [
            ("常见错误①：漏写 WHERE 更新全表", "最常见的误操作，可能篡改大量数据", "最常见的错误是漏写 WHERE，结果把整张表的数据都改了，造成难以恢复的后果。"),
            ("常见错误②：SET 列与值类型不匹配", "新值类型必须与列定义一致", "如果 SET 的新值类型与列定义不一致，更新会失败或触发隐式转换导致结果异常。"),
        ],
        "compare": (
            "UPDATE 修改已有行；INSERT 新增行；DELETE 删除行，三者操作的数据对象不同。",
            "和 INSERT、DELETE 对比：UPDATE 修改已有行，INSERT 新增行，DELETE 删除行，三者操作的对象各不相同。",
        ),
        "transaction": (
            "UPDATE 受事务控制，批量更新建议先核对命中记录并在事务中提交。",
            "UPDATE 受事务控制，建议先用相同条件的查询核对命中记录，再把更新放在事务中，确认后再提交。",
        ),
        "perf": (
            "WHERE 条件列建索引避免全表更新；大批量更新应分批提交。",
            "性能方面，给 WHERE 条件列建立索引可以避免全表扫描和全表更新；大批量更新建议分批提交以降低锁的开销。",
        ),
        "review": (
            "定位目标行 → 加锁计算新值 → 更新并提交。",
            "回顾 UPDATE 的执行过程：先按条件定位目标行，再加锁计算新值，最后写回并在提交后生效。",
        ),
        "summary": (
            "UPDATE 修改已有数据行；SET 指定新值、WHERE 限定范围；省略 WHERE 会更新整表；受事务控制、可回滚。",
            "总结本节要点：UPDATE 用于修改已有数据行；SET 指定新值、WHERE 限定范围；省略 WHERE 会更新整张表；它受事务控制并且可以回滚。",
        ),
        "question": (
            "如果只想修改某一名学生的年龄，WHERE 条件应该怎么写？",
            "课后思考题：如果只想修改某一名学生的年龄，WHERE 条件应该怎么写才安全呢？",
        ),
    },
    "select": {
        "short": "SELECT",
        "name": "SELECT 语句：查询数据",
        "concept": (
            "SELECT 用于从表中查询数据，是数据查询语言 DQL 的核心语句。",
            "本节视频只讲解 SELECT 语句。SELECT 是数据查询语言 DQL 的核心，用来从表中检索数据，下面只围绕 SELECT 展开。",
        ),
        "purpose": (
            "按条件检索数据，支持过滤、分组、排序等操作。",
            "SELECT 的作用是从一张或多张表中检索满足条件的数据，并支持过滤、分组、排序等丰富功能。",
        ),
        "syntax": (
            "SELECT <列名> FROM <表名> [WHERE ...] [GROUP BY ...] [HAVING ...] [ORDER BY ...];",
            "SELECT 的完整语法包括 SELECT 指定列、FROM 指定表，后面还可以跟 WHERE、GROUP BY、HAVING 和 ORDER BY 等子句。",
        ),
        "clauses": (
            "WHERE 行级过滤；GROUP BY 分组；HAVING 分组过滤；ORDER BY 排序。",
            "各子句分工明确：WHERE 做行级过滤，GROUP BY 分组，HAVING 对分组结果过滤，ORDER BY 负责排序。",
        ),
        "steps": [
            ("执行流程①：FROM 定位数据源", "确定要查询的表或视图", "执行 SELECT 时，系统先从 FROM 子句确定数据来源，也就是要查询的表或视图。"),
            ("执行流程②：WHERE 过滤行", "按条件筛掉不符合要求的行", "然后 WHERE 子句对行进行过滤，把不符合条件的行先筛掉，减少后续处理的数据量。"),
            ("执行流程③：分组排序并输出", "GROUP BY/HAVING 处理分组，ORDER BY 排序后输出结果", "接着 GROUP BY 和 HAVING 处理分组与分组过滤，最后 ORDER BY 排序，按 SELECT 指定的列输出结果。"),
        ],
        "case_scene": (
            "学生表 Student 中，查询年龄大于 20 岁的学生姓名。",
            "看一个例子：在学生表 Student 中，查询年龄大于二十岁的学生姓名。",
        ),
        "case_sql": (
            "SELECT Sname FROM Student WHERE Sage > 20;",
            "对应的 SQL 是：SELECT Sname FROM Student WHERE Sage 大于 20，意思是只取年龄大于二十岁的学生姓名。",
        ),
        "case_result": (
            "只返回年龄大于 20 岁的学生姓名，其余不显示。",
            "执行后只返回年龄大于二十岁的学生姓名，其他学生不会出现在结果中。",
        ),
        "notes": [
            ("注意事项①：执行顺序与书写顺序不同", "FROM→WHERE→GROUP BY→HAVING→SELECT→ORDER BY", "注意 SELECT 的执行顺序和书写顺序不同：先 FROM，再 WHERE，然后 GROUP BY、HAVING，最后 SELECT 和 ORDER BY。"),
            ("注意事项②：聚合函数常与分组配合", "COUNT/SUM/AVG/MAX/MIN 用于分组统计", "COUNT、SUM、AVG、MAX、MIN 等聚合函数通常和 GROUP BY 配合使用，用于分组统计。"),
        ],
        "errors": [
            ("常见错误①：WHERE 中误用聚合函数", "聚合条件应写在 HAVING 中", "常见错误是在 WHERE 中直接使用聚合函数，聚合条件应当写在 HAVING 子句中。"),
            ("常见错误②：LIKE 通配符使用不当", "%匹配任意长度，_只匹配单个字符", "使用 LIKE 模糊查询时容易混淆通配符：百分号匹配任意长度字符串，下划线只匹配单个字符。"),
        ],
        "compare": (
            "SELECT 只读不修改数据；INSERT/UPDATE/DELETE 会改变数据。",
            "和 DML 的其它三条语句对比：SELECT 只读取数据、不修改数据，而 INSERT、UPDATE、DELETE 都会实际改变表中的数据。",
        ),
        "transaction": (
            "SELECT 通常不加锁或只加共享锁，一般不改变数据。",
            "SELECT 一般只读取数据，通常不加锁或只加共享锁，不会改变数据，因此也常被用来在执行修改前核对条件。",
        ),
        "perf": (
            "给 WHERE 和连接列建索引可显著提升查询速度。",
            "性能方面，给 WHERE 条件和连接列建立索引可以显著提升查询速度，减少全表扫描。",
        ),
        "review": (
            "FROM 定位数据源 → WHERE 过滤行 → 分组排序后输出。",
            "回顾 SELECT 的执行过程：FROM 定位数据源，WHERE 过滤行，然后分组、排序并输出结果。",
        ),
        "summary": (
            "SELECT 是查询数据的核心语句；支持 WHERE、GROUP BY、HAVING、ORDER BY；聚合函数配合分组统计；只读操作，常用于修改前核对。",
            "总结本节要点：SELECT 是查询数据的核心语句，支持过滤、分组、排序等子句，聚合函数常配合分组使用，而且它只读不修改，常用于修改前的条件核对。",
        ),
        "question": (
            "SELECT 的执行顺序与书写顺序有什么不同？",
            "课后思考题：SELECT 语句的执行顺序和书写顺序有什么不同呢？请结合本节内容思考一下。",
        ),
    },
}


# 每条语句自身负责的数据操作范围（用于单语句视频的“使用边界”页）
_STATEMENT_SCOPE = {
    "insert": "新增数据",
    "update": "修改已有数据",
    "delete": "删除已有数据",
    "select": "读取数据并返回结果集",
}


def _build_statement_slides(key: str) -> list:
    """为单条 SQL 语句生成 20 页、只围绕该语句的 PPT 内容。"""
    data = _STATEMENT_VIDEO[key]
    short = data["short"]
    slides = []

    def add(title, content, speech):
        slides.append({
            "slide_number": len(slides) + 1,
            "title": title,
            "content": content,
            "speech": speech,
            "duration": SECONDS_PER_SLIDE,
        })

    content, speech = data["concept"]
    add(f"{short} 是什么", content, speech)
    content, speech = data["purpose"]
    add(f"{short} 的作用", content, speech)
    content, speech = data["syntax"]
    add(f"{short} 语法格式", content, speech)
    content, speech = data["clauses"]
    add(f"{short} 语法要点", content, speech)
    for title, content, speech in data["steps"]:
        add(title, content, speech)
    content, speech = data["case_scene"]
    add("教材案例：场景", content, speech)
    content, speech = data["case_sql"]
    add("教材案例：SQL", content, speech)
    content, speech = data["case_result"]
    add("教材案例：结果与分析", content, speech)
    for title, content, speech in data["notes"]:
        add(title, content, speech)
    for title, content, speech in data["errors"]:
        add(title, content, speech)
    # 单语句视频只讲这一条语句本身，不做与其它语句的对比，改用“使用边界”页面占位
    scope = _STATEMENT_SCOPE.get(key, "处理数据")
    add(
        f"{short} 的使用边界",
        f"只负责{scope}，不会改变表中其它数据",
        f"最后明确{short}的使用边界：它只负责{scope}，执行时不会影响表中其它的数据。"
        f"把职责看清楚，就不会把它和别的操作混在一起使用。",
    )
    content, speech = data["transaction"]
    add("事务与安全性", content, speech)
    content, speech = data["perf"]
    add("性能与优化", content, speech)
    content, speech = data["review"]
    add("完整流程回顾", content, speech)
    content, speech = data["summary"]
    add("学习要点总结", content, speech)
    content, speech = data["question"]
    add("课后思考", content, speech)
    return slides[:SLIDES_COUNT]


def _build_generic_focused_slides(title: str, body: str) -> list:
    """对非 SQL 语句的小节，依据该小节正文生成只围绕它的 20 页 PPT。"""
    clean_title = re.sub(r"^[一二三四五六七八九十]+、", "", title or "").strip() or "知识点讲解"
    sentences = [s.strip() for s in re.split(r"[。！？；\n]", body or "") if len(s.strip()) >= 8]
    slides = []

    def add(slide_title, content, speech):
        slides.append({
            "slide_number": len(slides) + 1,
            "title": slide_title,
            "content": content,
            "speech": speech,
            "duration": SECONDS_PER_SLIDE,
        })

    add(f"{clean_title} · 概念引入", clean_title, f"本次视频只讲解{clean_title}这一小节的内容，下面开始讲解。")
    for idx, sentence in enumerate(sentences):
        add(f"{clean_title} · 要点{idx + 1}", sentence[:60], sentence)
        if len(slides) >= SLIDES_COUNT - 4:
            break

    fillers = [
        (f"{clean_title} · 关键要点", f"梳理{clean_title}的关键要点", f"总结一下{clean_title}的关键要点，便于记忆和复习。"),
        (f"{clean_title} · 典型示例", f"结合示例理解{clean_title}", f"结合教材中的示例，可以更直观地理解{clean_title}。"),
        (f"{clean_title} · 注意事项", f"学习{clean_title}时的注意点", f"在学习{clean_title}时要注意其中的关键细节，避免混淆。"),
    ]
    filler_index = 0
    while len(slides) < SLIDES_COUNT - 1:
        slide_title, content, speech = fillers[filler_index % len(fillers)]
        add(slide_title, content, speech)
        filler_index += 1
    add(f"{clean_title} · 课后思考", f"关于{clean_title}你还有哪些疑问？", f"课后思考：关于{clean_title}，你还有哪些疑问和延伸的问题？")
    return slides[:SLIDES_COUNT]


def generate_focused_video_presentation(topic_title: str, topic_body: str, question_text: str = "") -> dict:
    """只围绕知识点内部某个小节生成视频，其他小节/知识点不涉及。"""
    clean_title = re.sub(r"^[一二三四五六七八九十]+、", "", topic_title or "").strip() or "知识点讲解"
    # 只用小节标题和用户提问判断是否指向 SQL 语句，避免小节正文里偶然出现的
    # “插入/更新/删除”等字样把非 SQL 小节误判成某条 SQL 语句的视频。
    statement_key = _detect_statement_english(f"{topic_title} {question_text}")
    if statement_key:
        slides = _build_statement_slides(statement_key)
        title = _STATEMENT_VIDEO[statement_key]["name"]
    else:
        slides = _build_generic_focused_slides(clean_title, topic_body)
        title = clean_title

    full_speech = " ".join(slide["speech"] for slide in slides)
    total_duration = sum(slide["duration"] for slide in slides)

    return {
        "media_type": "video",
        "format": "ppt_presentation",
        "title": title,
        "slides": slides,
        "full_speech": full_speech,
        "duration": f"{total_duration}秒",
        "duration_seconds": total_duration,
        "slides_count": len(slides),
    }


def generate_statement_video(question_text: str):
    """提问明确点名某条 SQL 语句（如“演示delete语句”）时，生成只讲解该语句的视频；识别不到返回 None。"""
    key = _detect_statement_english(question_text)
    if not key:
        return None
    slides = _build_statement_slides(key)
    full_speech = " ".join(slide["speech"] for slide in slides)
    total_duration = sum(slide["duration"] for slide in slides)
    return {
        "media_type": "video",
        "format": "ppt_presentation",
        "title": _STATEMENT_VIDEO[key]["name"],
        "slides": slides,
        "full_speech": full_speech,
        "duration": f"{total_duration}秒",
        "duration_seconds": total_duration,
        "slides_count": len(slides),
    }


def generate_video_presentation(knowledge_point: KnowledgePoint, question_text: str = "") -> dict:
    """生成完整的视频演示数据，包含PPT页面和音频解说脚本"""
    slides = generate_ppt_slides(knowledge_point, question_text)

    full_speech = " ".join([slide["speech"] for slide in slides])

    total_duration = sum(slide["duration"] for slide in slides)

    return {
        "media_type": "video",
        "format": "ppt_presentation",
        "title": knowledge_point.content,
        "slides": slides,
        "full_speech": full_speech,
        "duration": f"{total_duration}秒",
        "duration_seconds": total_duration,
        "slides_count": len(slides)
    }


def detect_video_keyword_topic(question_text: str):
    """识别提问中明确指向的数据库主题关键词，返回 (keyword, topic, category)；识别不到返回 None。"""
    lower_question = (question_text or "").lower()

    # 顺序即优先级：越具体的主题越靠前，避免“实体完整性”被“实体”劫持成 ER 模型视频
    keyword_topics = {
        'b+树': ('B+树索引结构', '索引'),
        'b树': ('B+树索引结构', '索引'),
        '死锁': ('死锁', '并发控制'),
        'acid': ('事务的ACID特性', '事务'),
        '事务': ('事务的ACID特性', '事务'),
        'sql': ('SQL语言', 'SQL'),
        'select': ('SELECT查询语句', 'SQL'),
        'insert': ('INSERT语句', 'SQL'),
        'update': ('UPDATE语句', 'SQL'),
        'delete': ('DELETE语句', 'SQL'),
        '范式': ('数据库范式', '关系数据理论'),
        '规范化': ('数据库范式', '关系数据理论'),
        '函数依赖': ('函数依赖与范式', '关系数据理论'),
        '完整性': ('数据库完整性', '完整性'),
        '安全性': ('数据库安全性', '安全性'),
        '恢复': ('数据库恢复技术', '恢复技术'),
        '日志': ('数据库恢复技术', '恢复技术'),
        'mvcc': ('MVCC多版本并发控制', '并发控制'),
        '并发': ('并发控制', '并发控制'),
        '锁': ('封锁与并发控制', '并发控制'),
        'er图': ('ER模型', '数据库设计'),
        'e-r模型': ('ER模型', '数据库设计'),
        '实体联系': ('ER模型', '数据库设计'),
    }

    for keyword, (topic, category) in keyword_topics.items():
        if keyword in lower_question:
            return (keyword, topic, category)

    return None


def generate_video_by_keywords(question_text: str) -> dict:
    """根据关键词直接生成视频（不依赖数据库知识点）"""
    matched = detect_video_keyword_topic(question_text)
    if not matched:
        return None
    _keyword, topic, category = matched
    fake_kp = type('FakeKnowledgePoint', (), {
        'content': topic,
        'category': category,
        'detail_content': '',
        'key_points': []
    })()
    return generate_video_presentation(fake_kp, question_text)
