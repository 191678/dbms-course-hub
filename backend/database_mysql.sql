CREATE DATABASE IF NOT EXISTS dbms_course_hub DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE dbms_course_hub;

CREATE TABLE IF NOT EXISTS chapters (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '章节ID',
    title VARCHAR(200) NOT NULL COMMENT '章节标题',
    description TEXT COMMENT '章节描述',
    order_index INT NOT NULL DEFAULT 0 COMMENT '排序索引',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_chapters_order (order_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='章节表';

CREATE TABLE IF NOT EXISTS knowledge_points (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '知识点ID',
    chapter_id INT NOT NULL COMMENT '关联章节ID',
    content TEXT NOT NULL COMMENT '知识点内容',
    difficulty VARCHAR(20) NOT NULL DEFAULT 'medium' COMMENT '难度等级：easy/medium/hard',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_knowledge_points_chapter (chapter_id),
    INDEX idx_knowledge_points_difficulty (difficulty),
    CONSTRAINT fk_knowledge_points_chapter FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识点表';

CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '题目ID',
    knowledge_point_id INT NOT NULL COMMENT '关联知识点ID',
    type VARCHAR(20) NOT NULL COMMENT '题目类型：单选/多选/判断/SQL编程',
    stem TEXT NOT NULL COMMENT '题目题干',
    options JSON COMMENT '选项（JSON格式）',
    answer TEXT NOT NULL COMMENT '正确答案',
    analysis TEXT COMMENT '答案解析',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_questions_knowledge_point (knowledge_point_id),
    INDEX idx_questions_type (type),
    CONSTRAINT fk_questions_knowledge_point FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='题目表';

INSERT INTO chapters (title, description, order_index) VALUES 
('第一章 数据库系统概述', '本章介绍数据库系统的基本概念、发展历程和组成结构，帮助学生建立对数据库系统的整体认识。', 1),
('第二章 关系数据库基础', '本章讲解关系模型的基本概念、关系代数运算和关系完整性约束，是学习SQL的基础。', 2),
('第三章 SQL语言', '本章详细介绍SQL语言的各类语句，包括数据定义、数据查询、数据更新和视图操作等。', 3),
('第四章 数据库设计', '本章阐述数据库设计的全过程，包括需求分析、概念设计、逻辑设计和物理设计。', 4),
('第五章 数据库安全性', '本章讨论数据库安全的基本概念、访问控制、数据加密和审计技术。', 5);

INSERT INTO knowledge_points (chapter_id, content, difficulty) VALUES 
(1, '数据库系统的定义和组成', 'easy'),
(1, '数据管理技术的发展阶段', 'easy'),
(1, '数据库管理系统的功能', 'medium'),
(2, '关系模型的基本概念', 'easy'),
(2, '关系代数的基本运算', 'medium'),
(2, '关系的完整性约束', 'medium'),
(3, 'SELECT查询语句', 'medium'),
(3, 'WHERE条件过滤', 'easy'),
(3, 'GROUP BY分组聚合', 'medium'),
(3, 'JOIN多表连接', 'hard'),
(4, 'ER模型设计', 'medium'),
(4, '关系模式规范化', 'hard'),
(5, '数据库访问控制', 'medium'),
(5, '数据加密技术', 'hard');

INSERT INTO questions (knowledge_point_id, type, stem, options, answer, analysis) VALUES 
(1, '单选', '下列哪一项不是数据库系统的组成部分？', '["数据库", "数据库管理系统", "操作系统", "应用程序"]', 'C', '数据库系统由数据库、数据库管理系统、应用程序和用户组成，操作系统不属于数据库系统的直接组成部分。'),
(1, '判断', '数据库管理系统（DBMS）是数据库系统的核心软件。', NULL, '正确', 'DBMS负责数据库的建立、使用和维护，是数据库系统的核心组件。'),
(2, '单选', '关系代数中，选择运算的作用是？', '["从关系中选择列", "从关系中选择行", "将两个关系合并", "对关系进行排序"]', 'B', '选择运算（σ）是从关系中选择满足给定条件的元组（行）。'),
(2, '多选', '关系的完整性约束包括哪些？', '["实体完整性", "参照完整性", "用户定义完整性", "数据完整性"]', 'ABC', '关系的完整性约束包括实体完整性、参照完整性和用户定义完整性三类。'),
(3, '单选', 'SQL语句中，用于查询数据的关键字是？', '["INSERT", "UPDATE", "SELECT", "DELETE"]', 'C', 'SELECT关键字用于从数据库表中查询数据。'),
(3, 'SQL编程', '假设有学生表students(id, name, age, department)，请编写SQL语句查询每个部门的学生人数。', NULL, 'SELECT department, COUNT(*) AS student_count FROM students GROUP BY department;', '使用GROUP BY按部门分组，COUNT(*)统计每组的人数。'),
(4, '单选', '在ER模型中，矩形表示什么？', '["实体", "属性", "联系", "主键"]', 'A', '在ER图中，矩形表示实体，椭圆形表示属性，菱形表示联系。'),
(5, '判断', '数据库的安全性是指保护数据库以防止不合法使用所造成的数据泄露、更改或破坏。', NULL, '正确', '数据库安全性的目标就是保护数据库免受各类威胁。');
