"""
Seed data script for the DBMS Course Hub.
Populates the database with comprehensive test data:
- 30 student accounts
- 5 chapters with knowledge points
- 10 questions per knowledge point
- Study records for all students
- Course content, RBAC data, etc.

Run after database initialization:
    python -m app.seed_data
"""
import sys
import os
import random
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import (
    StudentUser, Chapter, KnowledgePoint, Question,
    StudyRecord, CourseContent, QuestionUsage,
    Role, Permission, UserRole, RolePermission,
    KnowledgePointTag, KnowledgePointTagRelation,
    StudentKnowledgePoint, VisualizationTemplate
)
from app.utils.auth import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

CHAPTERS_DATA = [
    {
        "title": "第一章 数据库系统概述",
        "description": "介绍数据库系统的基本概念、发展历史和体系结构",
        "knowledge_points": [
            {"content": "数据库的定义与特征", "difficulty": "easy", "category": "基础概念"},
            {"content": "数据库系统的三级模式结构", "difficulty": "medium", "category": "体系结构"},
            {"content": "数据库管理系统的功能与组成", "difficulty": "medium", "category": "系统组成"},
            {"content": "数据模型的三要素", "difficulty": "easy", "category": "数据模型"},
            {"content": "常见数据模型介绍（层次、网络、关系、面向对象）", "difficulty": "medium", "category": "数据模型"},
        ]
    },
    {
        "title": "第二章 关系模型与关系代数",
        "description": "关系模型的基本理论和关系代数运算",
        "knowledge_points": [
            {"content": "关系模型的基本概念（关系、元组、属性、码）", "difficulty": "easy", "category": "关系模型"},
            {"content": "关系的完整性约束（实体完整性、参照完整性、用户定义完整性）", "difficulty": "medium", "category": "完整性"},
            {"content": "关系代数的基本运算（选择、投影、并、差、笛卡尔积）", "difficulty": "medium", "category": "关系代数"},
            {"content": "关系代数的扩展运算（连接、自然连接、除）", "difficulty": "hard", "category": "关系代数"},
            {"content": "关系代数表达式的优化", "difficulty": "hard", "category": "查询优化"},
        ]
    },
    {
        "title": "第三章 SQL语言",
        "description": "SQL语言的语法和使用方法",
        "knowledge_points": [
            {"content": "SQL的数据定义语言（DDL）", "difficulty": "easy", "category": "SQL基础"},
            {"content": "SQL的数据操纵语言（DML）- 查询", "difficulty": "medium", "category": "SQL查询"},
            {"content": "SQL的数据操纵语言（DML）- 插入、更新、删除", "difficulty": "easy", "category": "SQL更新"},
            {"content": "SQL的聚集函数与分组查询", "difficulty": "medium", "category": "SQL高级"},
            {"content": "SQL的嵌套查询与集合运算", "difficulty": "hard", "category": "SQL高级"},
            {"content": "SQL的视图定义与使用", "difficulty": "medium", "category": "SQL高级"},
            {"content": "SQL的存储过程与触发器", "difficulty": "hard", "category": "SQL高级"},
        ]
    },
    {
        "title": "第四章 关系数据库设计",
        "description": "关系数据库的设计理论与方法",
        "knowledge_points": [
            {"content": "函数依赖的基本概念", "difficulty": "medium", "category": "范式理论"},
            {"content": "第一范式（1NF）、第二范式（2NF）", "difficulty": "easy", "category": "范式理论"},
            {"content": "第三范式（3NF）、BC范式（BCNF）", "difficulty": "medium", "category": "范式理论"},
            {"content": "第四范式（4NF）、第五范式（5NF）", "difficulty": "hard", "category": "范式理论"},
            {"content": "模式分解的无损连接性和保持函数依赖性", "difficulty": "hard", "category": "模式分解"},
            {"content": "数据库设计的全过程", "difficulty": "medium", "category": "设计方法"},
        ]
    },
    {
        "title": "第五章 事务与并发控制",
        "description": "事务管理和并发控制机制",
        "knowledge_points": [
            {"content": "事务的ACID特性", "difficulty": "easy", "category": "事务管理"},
            {"content": "封锁协议与两段锁协议", "difficulty": "medium", "category": "并发控制"},
            {"content": "可串行化调度与冲突可串行化", "difficulty": "hard", "category": "并发控制"},
            {"content": "多版本并发控制（MVCC）", "difficulty": "hard", "category": "并发控制"},
            {"content": "死锁的处理与预防", "difficulty": "medium", "category": "并发控制"},
            {"content": "数据库的恢复技术", "difficulty": "medium", "category": "恢复技术"},
        ]
    },
]

QUESTION_TEMPLATES = {
    "easy": {
        "单选": [
            {"stem": "下列关于{kp}的描述，正确的是？", "options": ["描述A", "描述B", "描述C", "描述D"], "answer": "A", "analysis": "正确答案是A，因为..."},
            {"stem": "{kp}的主要特征是什么？", "options": ["特征1", "特征2", "特征3", "特征4"], "answer": "B", "analysis": "正确答案是B，这是{kp}的核心特征。"},
            {"stem": "以下哪个选项不属于{kp}的范畴？", "options": ["选项1", "选项2", "选项3", "选项4"], "answer": "C", "analysis": "选项C不属于{kp}的范畴。"},
        ],
        "判断": [
            {"stem": "判断题：{kp}是数据库系统的基础概念。", "answer": "正确", "analysis": "{kp}确实是数据库系统的基础概念。"},
            {"stem": "判断题：{kp}与数据模型无关。", "answer": "错误", "analysis": "{kp}与数据模型密切相关。"},
        ],
    },
    "medium": {
        "单选": [
            {"stem": "关于{kp}，下列说法正确的是？", "options": ["说法A", "说法B", "说法C", "说法D"], "answer": "B", "analysis": "说法B正确。{kp}的核心原理是..."},
            {"stem": "{kp}在数据库设计中的作用是什么？", "options": ["作用A", "作用B", "作用C", "作用D"], "answer": "C", "analysis": "{kp}的主要作用是C。"},
            {"stem": "下列关于{kp}的比较，正确的是？", "options": ["比较A", "比较B", "比较C", "比较D"], "answer": "D", "analysis": "比较D正确地描述了{kp}的特点。"},
        ],
        "多选": [
            {"stem": "{kp}涉及的主要方面包括？（多选）", "options": ["方面A", "方面B", "方面C", "方面D"], "answer": "A,B,C", "analysis": "{kp}主要涉及A、B、C三个方面。"},
            {"stem": "关于{kp}，以下说法正确的是？（多选）", "options": ["说法1", "说法2", "说法3", "说法4"], "answer": "B,D", "analysis": "说法B和D正确。"},
        ],
    },
    "hard": {
        "单选": [
            {"stem": "{kp}的实现机制中，关键的技术细节是？", "options": ["细节A", "细节B", "细节C", "细节D"], "answer": "C", "analysis": "技术细节C是{kp}的关键实现。"},
            {"stem": "在复杂场景下，{kp}的最优策略是？", "options": ["策略A", "策略B", "策略C", "策略D"], "answer": "D", "analysis": "策略D在复杂场景下最优。"},
        ],
        "多选": [
            {"stem": "{kp}与相关技术的综合应用中，需要考虑的因素有？（多选）", "options": ["因素A", "因素B", "因素C", "因素D"], "answer": "A,B,C,D", "analysis": "所有因素都需要考虑。"},
            {"stem": "{kp}的高级特性包括？（多选）", "options": ["特性1", "特性2", "特性3", "特性4"], "answer": "A,C", "analysis": "特性A和C是{kp}的高级特性。"},
        ],
    },
}

STUDENT_NAMES = [
    ("2024001", "admin", "管理员", "admin"),
    ("2024002", "zhang_san", "张三", "student"),
    ("2024003", "li_si", "李四", "student"),
    ("2024004", "wang_wu", "王五", "student"),
    ("2024005", "zhao_liu", "赵六", "student"),
    ("2024006", "qian_qi", "钱七", "student"),
    ("2024007", "sun_ba", "孙八", "student"),
    ("2024008", "zhou_jiu", "周九", "student"),
    ("2024009", "wu_shi", "吴十", "student"),
    ("2024010", "zheng_shiyi", "郑十一", "student"),
    ("2024011", "wang_shier", "王十二", "student"),
    ("2024012", "feng_shisan", "冯十三", "student"),
    ("2024013", "chen_shisi", "陈十四", "student"),
    ("2024014", "chu_shiwu", "褚十五", "student"),
    ("2024015", "wei_shiliu", "卫十六", "student"),
    ("2024016", "jiang_shiqi", "蒋十七", "student"),
    ("2024017", "shen_shiba", "沈十八", "student"),
    ("2024018", "han_shijiu", "韩十九", "student"),
    ("2024019", "yang_ershi", "杨二十", "student"),
    ("2024020", "zhu_ershiyi", "朱二十一", "student"),
    ("2024021", "qin_ershier", "秦二十二", "student"),
    ("2024022", "you_ershisan", "尤二十三", "student"),
    ("2024023", "xu_ershisi", "许二十四", "student"),
    ("2024024", "he_ershiwu", "何二十五", "student"),
    ("2024025", "lv_ershiliu", "吕二十六", "student"),
    ("2024026", "shi_ershiqi", "施二十七", "student"),
    ("2024027", "zhang_ershiba", "张二十八", "student"),
    ("2024028", "kong_ershijiu", "孔二十九", "student"),
    ("2024029", "cao_sanshi", "曹三十", "student"),
    ("2024030", "yan_sanshiyi", "严三十一", "student"),
    ("2024031", "hua_sanshier", "华三十二", "student"),
    ("2024032", "jin_sanshisan", "金三十三", "student"),
    ("2024033", "wei_sanshisi", "魏三十四", "student"),
    ("2024034", "tao_sanshiwu", "陶三十五", "student"),
    ("2024035", "jiang_sanshiliu", "姜三十六", "teacher"),
]

def seed_students():
    existing = db.query(StudentUser).count()
    if existing >= len(STUDENT_NAMES):
        print(f"  学生账号已存在 ({existing}个)，跳过")
        return

    count = 0
    for sid, username, name, role in STUDENT_NAMES:
        existing_user = db.query(StudentUser).filter(StudentUser.student_id == sid).first()
        if not existing_user:
            user = StudentUser(
                student_id=sid,
                username=username,
                password_hash=hash_password("student123"),
                name=name,
                role=role,
                is_active=True,
                last_login_at=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            db.add(user)
            count += 1
    db.commit()
    print(f"  创建了 {count} 个学生账号")

def seed_chapters_and_knowledge_points():
    existing_chapters = db.query(Chapter).count()
    if existing_chapters >= len(CHAPTERS_DATA):
        print(f"  章节已存在 ({existing_chapters}个)，跳过")
        return {}

    kp_map = {}  # chapter_id -> [kp_ids]
    for ch_data in CHAPTERS_DATA:
        existing_ch = db.query(Chapter).filter(Chapter.title == ch_data["title"]).first()
        if existing_ch:
            chapter = existing_ch
        else:
            chapter = Chapter(
                title=ch_data["title"],
                description=ch_data["description"],
                order_index=CHAPTERS_DATA.index(ch_data)
            )
            db.add(chapter)
            db.flush()

        kp_ids = []
        for idx, kp_data in enumerate(ch_data["knowledge_points"]):
            existing_kp = db.query(KnowledgePoint).filter(
                KnowledgePoint.chapter_id == chapter.id,
                KnowledgePoint.content == kp_data["content"]
            ).first()
            if existing_kp:
                kp_ids.append(existing_kp.id)
            else:
                kp = KnowledgePoint(
                    chapter_id=chapter.id,
                    content=kp_data["content"],
                    difficulty=kp_data["difficulty"],
                    category=kp_data["category"],
                    order_index=idx,
                    detail_content=f"本节介绍{kp_data['content']}的相关内容。",
                    key_points=[kp_data["content"]],
                )
                db.add(kp)
                db.flush()
                kp_ids.append(kp.id)
        kp_map[chapter.id] = kp_ids
    db.commit()
    total_kps = sum(len(v) for v in kp_map.values())
    print(f"  创建了 {len(kp_map)} 个章节，{total_kps} 个知识点")
    return kp_map

def seed_questions(kp_map):
    total_needed = sum(len(v) for v in kp_map.values()) * 10
    existing = db.query(Question).count()
    if existing >= total_needed:
        print(f"  题目已存在 ({existing}个)，跳过")
        return

    count = 0
    for chapter_id, kp_ids in kp_map.items():
        for kp_id in kp_ids:
            kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
            if not kp:
                continue

            existing_q_count = db.query(Question).filter(Question.knowledge_point_id == kp_id).count()
            if existing_q_count >= 10:
                continue

            templates = QUESTION_TEMPLATES.get(kp.difficulty, QUESTION_TEMPLATES["easy"])
            q_index = existing_q_count

            for i in range(existing_q_count, 10):
                q_type = random.choice(["单选", "单选", "单选", "多选", "判断"])
                type_templates = templates.get(q_type, templates["单选"])
                template = type_templates[i % len(type_templates)]

                stem = template["stem"].replace("{kp}", kp.content)
                options = [opt.replace("{kp}", kp.content) for opt in template.get("options", [])]
                answer = template["answer"]
                analysis = template["analysis"].replace("{kp}", kp.content)

                q = Question(
                    knowledge_point_id=kp_id,
                    type=q_type,
                    difficulty=kp.difficulty,
                    stem=stem,
                    options=options if q_type != "判断" else None,
                    answer=answer,
                    analysis=analysis,
                    order_index=i,
                )
                db.add(q)
                count += 1

                usage = QuestionUsage(
                    question=q,
                    usage_count=random.randint(0, 50),
                    correct_count=random.randint(0, 40),
                    average_time_seconds=random.randint(30, 300),
                    difficulty_rating=random.uniform(1.0, 5.0),
                    last_used_at=datetime.now() - timedelta(days=random.randint(0, 30))
                )
                db.add(usage)

    db.commit()
    print(f"  创建了 {count} 道题目")

def seed_study_records():
    existing = db.query(StudyRecord).count()
    if existing >= 300:
        print(f"  学习记录已存在 ({existing}条)，跳过")
        return

    students = db.query(StudentUser).filter(StudentUser.role == "student").all()
    kps = db.query(KnowledgePoint).all()
    chapters = db.query(Chapter).all()

    if not students or not kps:
        print("  缺少学生或知识点数据，跳过学习记录创建")
        return

    count = 0
    today = date.today()
    for _ in range(300):
        student = random.choice(students)
        kp = random.choice(kps)
        chapter = db.query(Chapter).filter(Chapter.id == kp.chapter_id).first()
        study_date = today - timedelta(days=random.randint(0, 60))
        duration = random.randint(5, 120)

        record = StudyRecord(
            student_id=student.student_id,
            course_name="数据库系统概论",
            chapter_name=chapter.title if chapter else "",
            knowledge_point_id=kp.id,
            knowledge_point_content=kp.content,
            study_date=datetime.combine(study_date, datetime.min.time()),
            duration_minutes=duration,
            study_type=random.choice(["self", "class", "review", "exam"]),
            is_abnormal=duration < 5 or duration > 480,
            abnormal_reason="学习时间过短" if duration < 5 else "学习时间过长" if duration > 480 else None,
            source="auto"
        )
        db.add(record)
        count += 1

    db.commit()
    print(f"  创建了 {count} 条学习记录")

def seed_student_kps():
    existing = db.query(StudentKnowledgePoint).count()
    if existing >= 100:
        print(f"  学生知识点记录已存在 ({existing}条)，跳过")
        return

    students = db.query(StudentUser).filter(StudentUser.role == "student").all()
    kps = db.query(KnowledgePoint).all()

    count = 0
    for student in students:
        student_kps = random.sample(kps, min(len(kps), random.randint(3, 8)))
        for kp in student_kps:
            mastery = random.choices(
                ["not_started", "practicing", "mastered"],
                weights=[0.2, 0.5, 0.3]
            )[0]
            skp = StudentKnowledgePoint(
                student_id=student.student_id,
                knowledge_point_id=kp.id,
                mastery_level=mastery,
                difficulty_level=random.randint(1, 5),
                last_study_date=datetime.now() - timedelta(days=random.randint(0, 30)),
                study_count=random.randint(0, 20),
                total_study_minutes=random.randint(0, 300)
            )
            db.add(skp)
            count += 1
    db.commit()
    print(f"  创建了 {count} 条学生知识点记录")

def seed_course_content():
    existing = db.query(CourseContent).count()
    if existing >= 20:
        print(f"  课程内容已存在 ({existing}条)，跳过")
        return

    kps = db.query(KnowledgePoint).all()
    chapters = db.query(Chapter).all()

    content_types = ["chapter_intro", "theory", "example", "exercise", "summary"]
    statuses = ["published", "published", "published", "draft", "archived"]

    count = 0
    for chapter in chapters:
        for _ in range(2):
            ct = random.choice(content_types)
            status = random.choice(statuses)
            cc = CourseContent(
                content_type=ct,
                title=f"{chapter.title} - {ct}",
                content=f"本章节介绍{chapter.title}的相关内容，涵盖了{ct}的核心知识点...",
                content_metadata={"order": count, "word_count": random.randint(100, 2000)},
                status=status,
                chapter_id=chapter.id,
                created_by=1,
                published_at=datetime.now() - timedelta(days=random.randint(0, 90)) if status == "published" else None,
            )
            db.add(cc)
            count += 1

    for kp in kps:
        if random.random() < 0.3:
            ct = random.choice(["theory", "example", "exercise"])
            cc = CourseContent(
                content_type=ct,
                title=f"{kp.content} - {ct}讲解",
                content=f"针对{kp.content}的{ct}详细讲解...",
                status="published",
                chapter_id=kp.chapter_id,
                knowledge_point_id=kp.id,
                created_by=1,
                published_at=datetime.now() - timedelta(days=random.randint(0, 60))
            )
            db.add(cc)
            count += 1

    db.commit()
    print(f"  创建了 {count} 条课程内容")

def seed_viz_templates():
    existing = db.query(VisualizationTemplate).count()
    if existing >= 5:
        print(f"  可视化模板已存在 ({existing}个)，跳过")
        return

    templates = [
        {"name": "知识点掌握度饼图", "chart_type": "pie", "config": {"series": ["掌握", "学习中", "未开始"], "colors": ["#67c23a", "#e6a23c", "#f56c6c"]}},
        {"name": "学习趋势折线图", "chart_type": "line", "config": {"x_axis": "日期", "y_axis": "学习时长(分钟)"}},
        {"name": "章节进度柱状图", "chart_type": "bar", "config": {"x_axis": "章节", "y_axis": "完成率(%)"}},
        {"name": "知识点雷达图", "chart_type": "radar", "config": {"indicators": ["基础", "进阶", "应用", "分析", "评价"]}},
        {"name": "学习热力图", "chart_type": "heatmap", "config": {"x_axis": "时间", "y_axis": "知识点", "color_range": [0, 100]}},
    ]

    count = 0
    for t in templates:
        vt = VisualizationTemplate(
            name=t["name"],
            chart_type=t["chart_type"],
            config=t["config"],
            is_public=True,
            created_by=1
        )
        db.add(vt)
        count += 1
    db.commit()
    print(f"  创建了 {count} 个可视化模板")

def seed_kp_tags():
    existing = db.query(KnowledgePointTag).count()
    if existing >= 5:
        print(f"  知识点标签已存在 ({existing}个)，跳过")
        return

    tags = [
        {"name": "重点", "category": "importance", "color": "#f56c6c"},
        {"name": "难点", "category": "difficulty", "color": "#e6a23c"},
        {"name": "常考点", "category": "exam", "color": "#409eff"},
        {"name": "易混点", "category": "caution", "color": "#f0a020"},
        {"name": "核心概念", "category": "type", "color": "#67c23a"},
    ]

    for t_data in tags:
        existing_tag = db.query(KnowledgePointTag).filter(KnowledgePointTag.name == t_data["name"]).first()
        if not existing_tag:
            tag = KnowledgePointTag(
                name=t_data["name"],
                category=t_data["category"],
                color=t_data["color"]
            )
            db.add(tag)
    db.commit()

    kps = db.query(KnowledgePoint).all()
    all_tags = db.query(KnowledgePointTag).all()

    for kp in kps:
        num_tags = random.randint(0, 2)
        selected_tags = random.sample(all_tags, num_tags) if all_tags else []
        for tag in selected_tags:
            skp = db.query(StudentKnowledgePoint).filter(
                StudentKnowledgePoint.knowledge_point_id == kp.id
            ).first()
            if skp:
                rel = KnowledgePointTagRelation(
                    student_kp_id=skp.id,
                    tag_id=tag.id
                )
                db.add(rel)

    db.commit()
    print(f"  创建了 {len(tags)} 个知识点标签")

def seed_rbac():
    from app.utils.permissions import init_rbac_data
    init_rbac_data(db)
    print("  RBAC 权限数据已初始化")

def main():
    print("=" * 50)
    print("开始填充种子数据...")
    print("=" * 50)

    try:
        print("\n[1/8] 学生账号")
        seed_students()

        print("\n[2/8] 章节与知识点")
        kp_map = seed_chapters_and_knowledge_points()

        print("\n[3/8] 题库 (每知识点10题)")
        seed_questions(kp_map)

        print("\n[4/8] 学习记录")
        seed_study_records()

        print("\n[5/8] 学生知识点")
        seed_student_kps()

        print("\n[6/8] 课程内容")
        seed_course_content()

        print("\n[7/8] 可视化模板与知识点标签")
        seed_viz_templates()
        seed_kp_tags()

        print("\n[8/8] RBAC 权限")
        seed_rbac()

        print("\n" + "=" * 50)
        print("种子数据填充完成！")
        print("=" * 50)

        stats = {
            "学生": db.query(StudentUser).count(),
            "章节": db.query(Chapter).count(),
            "知识点": db.query(KnowledgePoint).count(),
            "题目": db.query(Question).count(),
            "学习记录": db.query(StudyRecord).count(),
            "课程内容": db.query(CourseContent).count(),
            "知识点标签": db.query(KnowledgePointTag).count(),
            "可视化模板": db.query(VisualizationTemplate).count(),
            "角色": db.query(Role).count(),
            "权限": db.query(Permission).count(),
        }
        print("\n数据统计:")
        for k, v in stats.items():
            print(f"  {k}: {v}")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
