from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Chapter, KnowledgePoint, Question, AgentChatHistory
from app.schemas import ChatRequest, ChatResponse, VisualizeRequest, VisualizationResponse, VisualizationDiagram, SlidesAudioRequest, SlidesAudioResponse, AgentHistoryResponse, AgentHistoryItem
from app.knowledge_base import get_knowledge_from_db, generate_tts_audio
from app.agent.tools_simple import generate_mermaid_script_simple, generate_image_url, SIMPLE_MERMAID_TEMPLATES
from app.agent.tools import generate_animation_script, generate_video_presentation, generate_video_by_keywords, generate_focused_video_presentation, generate_statement_video, detect_video_keyword_topic
import json
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 每个账户最多保留的提问条数
MAX_AGENT_HISTORY = 5


def save_agent_question(db: Session, student_id: str, question: str) -> None:
    """按账户记录提问历史：同一账户最多保留最近 MAX_AGENT_HISTORY 条。

    相同问题会被去重并更新为最新提问时间，账户之间数据互相隔离。
    """
    if not student_id or not question:
        return
    student_id = student_id.strip()
    question = question.strip()
    if not student_id or not question:
        return

    try:
        existing = db.query(AgentChatHistory).filter(
            AgentChatHistory.student_id == student_id,
            AgentChatHistory.question == question
        ).all()
        for row in existing:
            db.delete(row)

        db.add(AgentChatHistory(student_id=student_id, question=question))
        db.flush()

        keep_ids = [
            row.id for row in db.query(AgentChatHistory.id)
            .filter(AgentChatHistory.student_id == student_id)
            .order_by(AgentChatHistory.created_at.desc(), AgentChatHistory.id.desc())
            .limit(MAX_AGENT_HISTORY)
            .all()
        ]
        if keep_ids:
            db.query(AgentChatHistory).filter(
                AgentChatHistory.student_id == student_id,
                AgentChatHistory.id.notin_(keep_ids)
            ).delete(synchronize_session=False)

        db.commit()
    except Exception as e:  # 历史记录写入失败不应影响正常问答
        db.rollback()
        logger.warning(f"保存提问历史失败: {e}")


def generate_media_by_keywords(question_text: str) -> dict:
    lower_question = question_text.lower()
    
    keyword_to_template = {
        'select语句': 'select_statement',
        'select查询': 'select_statement',
        '查询语句': 'select_statement',
        'select子句': 'select_statement',
        'b+树': 'bplus_tree',
        'b树': 'bplus_tree',
        'er模型转换': 'er_to_relation',
        'e-r模型转': 'er_to_relation',
        'er转关系': 'er_to_relation',
        '概念模型转': 'er_to_relation',
        'er图': 'er_diagram',
        '实体': 'er_diagram',
        '概念模型': 'er_diagram',
        '关系代数': 'relational_algebra',
        '选择运算': 'relational_algebra',
        '投影运算': 'relational_algebra',
        '笛卡尔积': 'relational_algebra',
        '连接运算': 'relational_algebra',
        '除运算': 'relational_algebra',
        '死锁': 'deadlock',
        'mvcc': 'mvcc_version',
        '版本链': 'mvcc_version',
        '多版本': 'mvcc_version',
        '两段锁': 'two_phase_lock',
        '2pl': 'two_phase_lock',
        '锁的类型': 'lock_types',
        '共享锁': 'lock_types',
        '排他锁': 'lock_types',
        's锁': 'lock_types',
        'x锁': 'lock_types',
        '并发操作': 'concurrency_problems',
        '脏读': 'concurrency_problems',
        '不可重复读': 'concurrency_problems',
        '幻读': 'concurrency_problems',
        '事务隔离': 'transaction_isolation',
        '隔离级别': 'transaction_isolation',
        '事务状态': 'transaction_state',
        '状态转换': 'transaction_state',
        'acid': 'acid',
        '三级模式': 'three_level_schema',
        '二级映像': 'three_level_schema',
        '二级映象': 'three_level_schema',
        '外模式': 'three_level_schema',
        '概念模式': 'three_level_schema',
        '内模式': 'three_level_schema',
        '数据库系统': 'database_system',
        'dbms': 'database_system',
        '数据模型': 'data_model',
        '层次模型': 'data_model',
        '网状模型': 'data_model',
        '关系模型': 'data_model',
        '查询优化': 'query_optimization',
        'sql优化': 'query_optimization',
        '代数优化': 'query_optimization',
        '物理优化': 'query_optimization',
        '数据库设计': 'database_design',
        '概念结构设计': 'database_design',
        '逻辑结构设计': 'database_design',
        '物理结构设计': 'database_design',
        '需求分析': 'database_design',
        '安全性': 'database_security_full',
        '存取控制': 'database_security_full',
        'grant': 'database_security_full',
        'revoke': 'database_security_full',
        '自主存取': 'database_security_full',
        '强制存取': 'database_security_full',
        'dac': 'database_security_full',
        'mac': 'database_security_full',
        '完整性': 'database_integrity',
        '实体完整性': 'database_integrity',
        '参照完整性': 'database_integrity',
        '外键': 'database_integrity',
        '数据类型': 'sql_data_types',
        'sql数据定义': 'sql_data_types',
        'create table': 'sql_data_types',
        'sql': 'sql_statements',
        'ddl': 'sql_statements',
        'dml': 'sql_statements',
        'dcl': 'sql_statements',
        '数据定义': 'sql_statements',
        '数据操纵': 'sql_statements',
        'select': 'sql_statements',
        '查询': 'sql_statements',
        'where': 'sql_statements',
        'group by': 'sql_statements',
        'order by': 'sql_statements',
        '恢复': 'database_recovery',
        '日志': 'database_recovery',
        '检查点': 'database_recovery',
        '转储': 'database_recovery',
        '数据依赖': 'dependency_normalization',
        '函数依赖': 'dependency_normalization',
        '多值依赖': 'dependency_normalization',
        '连接依赖': 'dependency_normalization',
        '范式': 'normalization_process',
        '规范化': 'normalization_process',
        'join': 'join_types',
        '连接': 'join_types',
        '事务': 'transaction_concurrency',
        '并发控制': 'transaction_concurrency',
        '锁': 'lock_protocol',
        '协议': 'lock_protocol',
        '索引': 'index_structure',
    }
    
    for keyword, template_key in keyword_to_template.items():
        if keyword in lower_question:
            if template_key in SIMPLE_MERMAID_TEMPLATES:
                template = SIMPLE_MERMAID_TEMPLATES[template_key]
                return {
                    "media_type": "image",
                    "format": "mermaid",
                    "content": template['script'],
                    "title": template['title']
                }
    
    return None


# detail_content 中的小节标题：一、二、… 或 【实际应用案例】 等
_SECTION_SPLIT_RE = re.compile(r"(?:^|\n)\s*([一二三四五六七八九十]+、[^\n]*|【[^】\n]+】)")


def _split_detail_sections(detail: str) -> list:
    if not detail:
        return []
    matches = list(_SECTION_SPLIT_RE.finditer(detail))
    if not matches:
        return [(None, detail.strip())]
    sections = []
    for idx, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(detail)
        sections.append((heading, detail[start:end].strip()))
    return sections


_VIDEO_TRIGGER_WORDS = [
    "视频讲解", "讲解视频", "生成视频", "演示", "视频", "动画", "讲解", "展示",
    "帮我", "给我", "请", "一下", "一个", "的",
]

# 这几类关键词已由“SQL 语句聚焦视频”专门处理，不参与关键词主题兜底
_SQL_STATEMENT_KEYWORDS = ('sql', 'select', 'insert', 'update', 'delete')


def _extract_subtopic_keyword(question: str) -> str:
    """从“演示实体完整性”这类提问中剥离触发词，提取用户真正指向的主题词。"""
    text = (question or "").strip()
    for word in _VIDEO_TRIGGER_WORDS:
        text = text.replace(word, "")
    return re.sub(r"[，。！？、（）()：:;；\"'“”\s]", "", text).strip()


def _select_named_section(question: str, detail: str):
    """提问直接点名小节标题或正文中的子主题时，返回对应内容。

    例如知识点“关系的完整性约束”的正文里含有“实体完整性”，
    提问“演示实体完整性”应当聚焦到实体完整性这一段，而不是整条知识点。
    """
    if not detail:
        return None
    normalized_question = _normalize_text(question)
    if not normalized_question:
        return None

    # 1) 小节标题命中（标题去掉“一、”“【】”等修饰后出现在提问中）
    best = None
    for heading, body in _split_detail_sections(detail):
        if not heading:
            continue
        title_text = re.sub(r"^[一二三四五六七八九十]+、", "", heading).strip("【】 ")
        normalized_heading = _normalize_text(title_text)
        if not normalized_heading or len(normalized_heading) < 2:
            continue
        if normalized_heading in normalized_question and (best is None or len(normalized_heading) > best[0]):
            best = (len(normalized_heading), heading, body)
    if best:
        return (best[1], best[2])

    # 2) 子主题命中：提问中的主题词出现在正文里，则抽取包含该主题词的句子
    keyword = _extract_subtopic_keyword(question)
    if 2 <= len(keyword) <= 12 and keyword in detail:
        sentences = [
            s.strip() for s in re.split(r"[。！？；\n]", detail)
            if keyword in s and len(s.strip()) >= 6
        ]
        if sentences:
            body = "。".join(sentences)
            return (keyword, body[:500])
    return None


def _select_focused_section(question: str, detail: str):
    """问题明显指向知识点内部某小节时，返回该小节，使回答更聚焦而非整段返回。"""
    normalized_question = _normalize_text(question)
    sections = _split_detail_sections(detail)
    if not normalized_question or len(sections) < 2:
        return None

    question_bigrams = _bigrams(normalized_question)
    question_tokens = re.findall(r"[a-zA-Z]{3,}", question.lower())

    scored = []
    token_hit = False
    for heading, body in sections:
        heading_text = (heading or "")
        score = 0
        heading_overlap = len(question_bigrams & _bigrams(_normalize_text(heading_text)))
        body_overlap = len(question_bigrams & _bigrams(_normalize_text(body)))
        score += heading_overlap * 3 + body_overlap
        for token in question_tokens:
            if token in heading_text.lower():
                score += 3
                token_hit = True
            elif token in body.lower():
                score += 1
                token_hit = True
        scored.append((score, heading, body))

    scored.sort(key=lambda item: item[0], reverse=True)
    top_score, top_heading, top_body = scored[0]
    second_score = scored[1][0]

    # 仅在小节优势明显时才聚焦：问题点到了具体小节名(英文关键词)，或问题非常短
    focused_allowed = token_hit or (not question_tokens and len(normalized_question) <= 8)
    if focused_allowed and top_score >= 4 and top_score >= second_score * 1.8:
        return (top_heading or "知识点讲解", top_body)
    return None


def _select_key_points(question: str, key_points: list) -> list:
    """挑选与问题相关的关键要点；若都无关则返回全部。"""
    if not key_points:
        return []
    normalized_question = _normalize_text(question)
    question_bigrams = _bigrams(normalized_question)
    question_tokens = re.findall(r"[a-zA-Z]{3,}", str(question).lower())
    selected = []
    for point in key_points:
        text = str(point)
        score = len(question_bigrams & _bigrams(_normalize_text(text)))
        for token in question_tokens:
            if token in text.lower():
                score += 3
        if score > 0:
            selected.append(text)
    return selected if selected else [str(p) for p in key_points]


def _is_sql_knowledge(kp) -> bool:
    """判断知识点是否属于 SQL 语言相关，用于限定“针对某条语句生成视频”的适用范围。"""
    text = f"{kp.content or ''} {kp.category or ''}".lower()
    return any(t in text for t in ["sql", "dml", "ddl", "dcl", "dql", "操纵", "查询", "数据定义", "数据控制"])


def _is_whole_knowledge_point(concept: str, question: str) -> bool:
    """判断提问是否指向整个知识点（与标题一致/包含标题/是标题中的缩写）。"""
    normalized_question = _normalize_text(question)
    normalized_concept = _normalize_text(concept)
    if not normalized_concept:
        return False
    is_acronym = bool(re.fullmatch(r"[a-z0-9]+", normalized_question))
    return (
        normalized_question == normalized_concept
        or (len(normalized_question) >= 6 and normalized_concept in normalized_question)
        or (is_acronym and normalized_question in normalized_concept)
    )


def generate_knowledge_response(knowledge: dict, question: str = "") -> str:
    concept = knowledge.get("concept", "")
    category = knowledge.get("category")
    detail = knowledge.get("definition") or ""
    key_points = knowledge.get("key_points") or []

    # 问题问的就是整个知识点（与标题一致/包含标题/是标题中的缩写）时，返回完整讲解
    is_whole_kp = _is_whole_knowledge_point(concept, question)

    focused = None if is_whole_kp else _select_focused_section(question, detail)

    answer = f"## {concept}\n\n"
    if category:
        answer += f"**分类**：{category}\n\n"

    if focused:
        heading, body = focused
        answer += f"**{heading}**：{body}\n\n"
        points = _select_key_points(question, key_points)
        if points:
            answer += "**关键要点**：\n"
            for i, point in enumerate(points, 1):
                answer += f"{i}. {point}\n"
            answer += "\n"
        return answer

    if detail:
        answer += f"**定义**：{detail}\n\n"
    if key_points:
        answer += "**关键要点**：\n"
        for i, point in enumerate(key_points, 1):
            answer += f"{i}. {point}\n"
        answer += "\n"
    return answer


def generate_questions(knowledge_point_id: int = None, count: int = 1, db: Session = None) -> dict:
    questions = []
    
    if knowledge_point_id and db:
        query = db.query(Question).filter(Question.knowledge_point_id == knowledge_point_id)
        questions_db = query.limit(count * 3).all()
        
        for q in questions_db:
            options = []
            if q.options:
                try:
                    options = json.loads(q.options) if isinstance(q.options, str) else q.options
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse options for question {q.id}: {e}")
                    pass
            
            questions.append({
                "id": q.id,
                "type": q.type,
                "stem": q.stem,
                "options": options,
                "answer": q.answer,
                "analysis": q.analysis
            })
    
    if not questions:
        question_templates = {
            "default": [
                {"type": "单选", "stem": "数据库系统的核心是？", "options": ["数据库", "数据库管理系统(DBMS)", "操作系统", "应用程序"], "answer": "B", "analysis": "数据库管理系统(DBMS)是数据库系统的核心软件。"},
                {"type": "多选", "stem": "以下哪些是事务的ACID特性？", "options": ["原子性(Atomicity)", "一致性(Consistency)", "独立性(Independence)", "持久性(Durability)"], "answer": "ABD", "analysis": "ACID包括原子性(A)、一致性(C)、隔离性(I)、持久性(D)。"},
                {"type": "判断", "stem": "B+树的非叶子节点存储数据。", "options": [], "answer": "错误", "analysis": "B+树的非叶子节点只存储索引键，数据只在叶子节点。"}
            ]
        }
        
        questions = question_templates["default"]
    
    return {"success": True, "questions": questions}


# 口语化提问中的填充词，匹配时忽略（长词优先替换，避免被短词截断）
_QUESTION_FILLERS = sorted([
    "什么是", "是什么", "请解释", "解释一下", "解释", "简述", "介绍一下", "介绍",
    "说明一下", "说明", "讲一下", "讲解一下", "讲解", "请问", "帮我", "我想知道",
    "如何理解", "怎么理解", "的作用", "作用", "的意义", "意义", "的概念", "概念",
    "的原理", "原理", "的区别", "区别", "有哪些", "哪些", "为什么", "怎么", "如何",
    "什么", "一下", "请", "吗", "呢", "啊",
], key=len, reverse=True)

# 短词/缩写别名 -> 对应知识点标题中的特征串，用于短词与同义表达兜底匹配
_KP_ALIASES = {
    "acid": "ACID", "mvcc": "MVCC", "多版本": "MVCC", "版本链": "MVCC", "快照读": "MVCC",
    "2pl": "两段锁", "两段锁": "两段锁", "封锁协议": "封锁协议", "可串行化": "可串行化",
    "死锁": "死锁", "幻读": "并发问题", "脏读": "并发问题", "不可重复读": "并发问题",
    "隔离级别": "并发问题", "三级模式": "三级模式", "二级映像": "三级模式",
    "二级映象": "三级模式", "外模式": "三级模式", "概念模式": "三级模式", "内模式": "三级模式",
    "dbms": "数据库管理系统", "数据库管理系统": "数据库管理系统",
    "数据管理技术": "数据管理技术", "数据模型": "数据模型", "层次模型": "数据模型",
    "网状模型": "数据模型", "面向对象模型": "数据模型", "er模型": "E-R模型",
    "e-r模型": "E-R模型", "er图": "E-R模型", "实体联系": "E-R模型",
    "函数依赖": "函数依赖", "范式": "范式", "1nf": "1NF", "2nf": "2NF",
    "3nf": "3NF", "bcnf": "BCNF", "无损连接": "模式分解", "保持函数依赖": "模式分解",
    "模式分解": "模式分解", "ddl": "DDL", "数据定义": "DDL", "dml": "DML",
    "聚集函数": "聚集函数", "分组": "聚集函数", "嵌套查询": "嵌套查询", "视图": "视图",
    "存储过程": "存储过程", "触发器": "触发器", "嵌入式": "嵌入式SQL",
    "查询处理": "查询处理步骤", "执行计划": "查询处理步骤", "查询优化": "优化",
    "关系代数": "关系代数", "选择运算": "基本运算", "投影": "基本运算",
    "笛卡尔积": "基本运算", "自然连接": "扩展运算", "除运算": "扩展运算",
    "恢复": "恢复技术", "备份": "恢复技术", "日志": "恢复技术", "检查点": "恢复技术",
    "故障": "故障类型", "加密": "数据加密", "安全性": "安全性概述",
    "安全控制": "安全控制", "存取控制": "安全控制", "grant": "安全控制", "revoke": "安全控制",
    "完整性": "完整性", "概念结构设计": "概念结构设计", "逻辑结构设计": "逻辑结构设计",
    "物理设计": "物理设计", "数据库设计": "数据库设计的全过程",
}


def _normalize_text(text: str) -> str:
    t = (text or "").lower()
    for filler in _QUESTION_FILLERS:
        t = t.replace(filler, "")
    return re.sub(r"[\s\W_]+", "", t, flags=re.UNICODE)


def _bigrams(text: str) -> set:
    if not text:
        return set()
    if len(text) < 2:
        return {text}
    return {text[i:i + 2] for i in range(len(text) - 1)}


def _key_points_text(kp) -> str:
    if not kp.key_points:
        return ""
    try:
        points = json.loads(kp.key_points) if isinstance(kp.key_points, str) else kp.key_points
    except (json.JSONDecodeError, TypeError):
        return ""
    if not isinstance(points, list):
        return ""
    return " ".join(str(p) for p in points)


def auto_detect_knowledge_point(question_text: str, db: Session):
    """匹配问题对应的知识点，覆盖课程全部知识点。

    先按别名/标题做精准匹配，再结合标题、摘要、关键要点、详细内容做模糊打分，
    返回与问题最相关的知识点；确实无相关知识点时返回 None。
    """
    normalized_question = _normalize_text(question_text)
    if not normalized_question:
        return None

    question_bigrams = _bigrams(normalized_question)
    hit_aliases = [hint for alias, hint in _KP_ALIASES.items() if alias in normalized_question]

    best_kp = None
    best_score = 0.0

    for kp in db.query(KnowledgePoint).all():
        content = kp.content or ""
        title = _normalize_text(content)
        if not title:
            continue

        score = 0.0

        # 1) 标题精准命中
        if title in normalized_question:
            score += 8.0
        elif normalized_question in title:
            score += 6.0

        # 2) 标题字符二元组重合度：问题越聚焦标题，得分越高
        title_bigrams = _bigrams(title)
        if title_bigrams and question_bigrams:
            score += 4.0 * len(question_bigrams & title_bigrams) / len(title_bigrams)

        # 3) 别名命中：解决 ACID、MVCC、2PL、BCNF 等短词难以匹配的问题
        score += 5.0 * sum(1 for hint in hit_aliases if hint in content)

        # 4) 摘要 / 关键要点 / 详细内容 的重合度，作为补充信号
        for field_bigrams, cap, weight in (
            (_bigrams(_normalize_text(kp.summary or "")), 6, 1.0),
            (_bigrams(_normalize_text(_key_points_text(kp))), 6, 1.0),
            (_bigrams(_normalize_text(kp.detail_content or "")), 8, 0.5),
        ):
            if field_bigrams:
                score += min(len(question_bigrams & field_bigrams), cap) * weight

        if score > best_score:
            best_score = score
            best_kp = kp

    if best_kp is None or best_score < 1.5:
        return None

    return best_kp


@router.get("/test-knowledge/")
def test_knowledge(db: Session = Depends(get_db)):
    result = get_knowledge_from_db("ACID", db)
    return result


@router.post("/chat/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    tool_used = None
    media_data = None
    questions_data = None
    answer = ""
    
    question_text = request.student_question.strip()
    lower_question = question_text.lower()
    
    auto_kp = auto_detect_knowledge_point(question_text, db)
    
    image_keywords = ["画图", "画一下", "绘制", "图解", "示意图", "以图片的形式展示", "图片展示", "图片形式", "生成图片", "图片总结", "以图片的形式体现", "以图片的形式", "图片体现", "图片的形式"]
    video_keywords = ["演示", "动画", "过程", "步骤", "执行", "视频", "讲解视频", "生成视频", "视频讲解"]
    
    is_image_request = any(word in lower_question for word in image_keywords)
    is_video_request = any(word in lower_question for word in video_keywords)
    
    if is_image_request:
        tool_used = "generate_image"

        keyword_result = generate_media_by_keywords(question_text)
        if keyword_result:
            media_data = keyword_result
            answer = f"我已为你生成了{keyword_result['title']}的图解。"
        elif auto_kp:
            mermaid_result = generate_mermaid_script_simple(auto_kp, question_text)
            if mermaid_result:
                media_data = mermaid_result
                answer = f"我已为你生成了{mermaid_result['title']}的图解。"
            else:
                url_result = generate_image_url(auto_kp, question_text)
                media_data = url_result
                answer = "我已为你生成了一张图解，帮助你理解这个概念。"
        else:
            answer = "抱歉，我暂时无法为这个问题生成图解。你可以尝试询问数据库系统相关的概念，如B+树、事务ACID、死锁等。"

    elif is_video_request:
        tool_used = "generate_video"

        video_data = None
        video_error = None
        try:
            if auto_kp:
                # 1) 提问明确指向某一条 SQL 语句（如“演示delete语句”）时，只生成该语句的视频
                if _is_sql_knowledge(auto_kp):
                    video_data = generate_statement_video(question_text)

                is_whole_kp = _is_whole_knowledge_point(auto_kp.content, question_text)

                # 2) 提问点名了知识点内部的小节或子主题（如“演示实体完整性”），只讲这一小段
                if video_data is None and auto_kp.detail_content and not is_whole_kp:
                    named = _select_named_section(question_text, auto_kp.detail_content)
                    if named:
                        video_data = generate_focused_video_presentation(named[0], named[1], question_text)

                # 3) 提问指向知识点内部某个小节时，只生成该小节的视频
                if video_data is None and auto_kp.detail_content and not is_whole_kp:
                    focused = _select_focused_section(question_text, auto_kp.detail_content)
                    if focused:
                        heading, body = focused
                        video_data = generate_focused_video_presentation(heading, body, question_text)

                # 4) 提问明确点名的主题与已匹配知识点无关时（例如库里没有B+树知识点，
                #    提问却命中了DDL知识点），优先按关键词主题生成，避免张冠李戴
                if video_data is None:
                    matched_keyword = detect_video_keyword_topic(question_text)
                    if (matched_keyword
                            and matched_keyword[0] not in _SQL_STATEMENT_KEYWORDS
                            and matched_keyword[0] not in (auto_kp.content or "").lower()):
                        video_data = generate_video_by_keywords(question_text)

                # 5) 否则生成整个知识点的视频
                if video_data is None:
                    video_data = generate_video_presentation(auto_kp, question_text)
        except Exception as e:  # 单个知识点生成失败不应让整个问答接口报错
            video_data = None
            video_error = f"{type(e).__name__}: {e}"
            logger.exception("视频生成失败：%s", video_error)

        if video_data is not None:
            media_data = video_data
            answer = f"我已为你生成了{video_data['title']}的视频讲解，共{video_data['slides_count']}页PPT，时长{video_data['duration']}。"
        else:
            keyword_video = generate_video_by_keywords(question_text)
            if keyword_video:
                media_data = keyword_video
                answer = f"我已为你生成了{keyword_video['title']}的视频讲解，共{keyword_video['slides_count']}页PPT，时长{keyword_video['duration']}。"
            elif video_error:
                answer = f"视频生成失败（{video_error}）。请稍后重试，或换一种问法，例如“演示实体完整性”。"
            else:
                answer = (
                    f"抱歉，未找到与「{question_text}」匹配的视频模板。"
                    "请确认知识点名称是否准确，例如：实体完整性、参照完整性、B+树索引、事务ACID特性、死锁、DELETE语句。"
                )
    
    elif any(word in lower_question for word in ["出题", "考考我", "考考", "刷题", "练习", "出一道", "来道题", "生成题", "做题", "习题"]):
        tool_used = "generate_questions"
        kp_id = auto_kp.id if auto_kp else None
        result = generate_questions(kp_id, 1, db)
        if result.get("success"):
            questions_data = result["questions"]
            answer = f"我为你生成了{len(questions_data)}道练习题，请认真作答！"
        else:
            answer = "题目生成暂时不可用。"
    
    else:
        if auto_kp:
            tool_used = "generate_knowledge"
            result = get_knowledge_from_db(auto_kp.content, db)
            if result.get("success"):
                answer = generate_knowledge_response(result, question_text)
            else:
                answer = result.get("message", "暂未找到相关知识点")
        else:
            answer = "抱歉，我只能回答数据库系统相关的问题。请问你想了解哪方面的知识？\n\n"
            answer += "💡 **常见问题**：\n"
            answer += "1. 什么是事务的ACID特性？\n"
            answer += "2. B+树索引的优点是什么？\n"
            answer += "3. 什么是幻读？如何解决？\n"
            answer += "4. 解释一下CAP理论\n"
            answer += "5. MVCC是如何工作的？\n"
            answer += "\n请告诉我你想了解哪个问题，我会详细解答。"

    if request.student_id:
        save_agent_question(db, request.student_id, question_text)

    return ChatResponse(
        answer=answer,
        tool_used=tool_used,
        context=request.context,
        media_data=media_data,
        questions=questions_data
    )


@router.get("/history/{student_id}/", response_model=AgentHistoryResponse)
def get_agent_history(student_id: str, db: Session = Depends(get_db)):
    """获取指定账户最近提问的 5 个问题（账户之间互不互通）。"""
    rows = (
        db.query(AgentChatHistory)
        .filter(AgentChatHistory.student_id == student_id.strip())
        .order_by(AgentChatHistory.created_at.desc(), AgentChatHistory.id.desc())
        .limit(MAX_AGENT_HISTORY)
        .all()
    )
    items = [
        AgentHistoryItem(
            id=r.id,
            question=r.question,
            created_at=r.created_at.isoformat() if r.created_at else None
        )
        for r in rows
    ]
    return AgentHistoryResponse(student_id=student_id, questions=items)


@router.post("/generate-audio/")
async def generate_audio(request: dict):
    text = request.get("text", "")
    if not text:
        return {"error": "文本内容不能为空"}

    audio_url = await generate_tts_audio(text)

    if audio_url:
        return {"success": True, "audio_url": audio_url}
    else:
        return {"success": False, "error": "语音合成失败"}


@router.post("/generate-slides-audio/", response_model=SlidesAudioResponse)
async def generate_slides_audio(request: SlidesAudioRequest):
    """批量生成 PPT 幻灯片的 TTS 语音，用于视频讲解的音频合成。

    入参示例:
        {"slides": [{"speech": "第一张幻灯片解说词"}, ...]}

    返回示例:
        {"success": True, "audio_urls": ["data:audio/mp3;base64,...", ...]}
    """
    slides = request.slides
    if not slides:
        return SlidesAudioResponse(success=False, error="slides 不能为空", audio_urls=[], total=0, failed_indexes=[])

    import asyncio

    audio_urls: list = []
    errors: list = []

    # 并发限制为 4，避免一次性发起过多 TTS 请求
    semaphore = asyncio.Semaphore(4)

    async def _gen_one(speech_text: str) -> str:
        if not speech_text:
            return ""
        async with semaphore:
            try:
                return await generate_tts_audio(speech_text)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"TTS generation failed for slide: {e}")
                return ""

    tasks = [_gen_one(s.speech or "") for s in slides]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    for idx, url in enumerate(results):
        if url:
            audio_urls.append(url)
        else:
            audio_urls.append("")
            errors.append(idx)

    success = len(errors) == 0
    return SlidesAudioResponse(
        success=success,
        audio_urls=audio_urls,
        total=len(audio_urls),
        failed_indexes=errors,
    )


@router.post("/visualize/", response_model=VisualizationResponse)
def visualize_knowledge(request: VisualizeRequest, db: Session = Depends(get_db)):
    topic = request.topic.strip()
    if not topic:
        return VisualizationResponse(
            success=False,
            knowledge_point=None,
            chapter=None,
            category=None,
            definition=None,
            key_points=None,
            theory_content=None,
            diagram=None,
            relationship_explanation=None
        )
    
    matched_kp = auto_detect_knowledge_point(topic, db)
    
    if not matched_kp:
        return VisualizationResponse(
            success=False,
            knowledge_point=None,
            chapter=None,
            category=None,
            definition=None,
            key_points=None,
            theory_content=None,
            diagram=None,
            relationship_explanation=None
        )
    
    chapter = db.query(Chapter).filter(Chapter.id == matched_kp.chapter_id).first()
    chapter_title = chapter.title if chapter else None
    
    kp_result = get_knowledge_from_db(matched_kp.content, db)
    
    diagram = None
    mermaid_result = generate_mermaid_script_simple(matched_kp, topic)
    if mermaid_result:
        diagram = VisualizationDiagram(
            media_type=mermaid_result["media_type"],
            format=mermaid_result["format"],
            content=mermaid_result["content"],
            title=mermaid_result["title"]
        )
    
    relationship_explanation = generate_relationship_explanation(matched_kp, mermaid_result)
    
    return VisualizationResponse(
        success=True,
        knowledge_point=matched_kp.content,
        chapter=chapter_title,
        category=kp_result.get("category") or matched_kp.category,
        definition=kp_result.get("definition"),
        key_points=kp_result.get("key_points"),
        theory_content=kp_result.get("detail_content") or matched_kp.detail_content,
        diagram=diagram,
        relationship_explanation=relationship_explanation
    )


def generate_relationship_explanation(kp: KnowledgePoint, mermaid_result: dict) -> str:
    content = kp.content
    lower_content = content.lower()
    
    if any(keyword in lower_content for keyword in ['b+树', 'b树']):
        return "B+树是一种平衡的多路搜索树，所有数据都存储在叶子节点，非叶子节点只存储索引键。这种结构保证了树的高度平衡，使得查询效率稳定。叶子节点之间通过链表连接，便于范围查询。"
    elif any(keyword in lower_content for keyword in ['er图', '实体', '关系', '概念模型']):
        return "ER模型使用实体（矩形）、属性（椭圆形）和联系（菱形）来描述现实世界的概念。实体之间存在一对一、一对多、多对多等关系，通过联系连接。ER图是数据库概念设计的重要工具。"
    elif '死锁' in lower_content:
        return "死锁是指两个或多个事务互相等待对方释放资源，导致所有事务都无法继续执行。数据库系统通过死锁检测和解除机制来处理死锁问题。"
    elif 'mvcc' in lower_content or '版本链' in lower_content:
        return "MVCC通过维护数据的多个版本，使得读事务和写事务可以同时进行而不需要加锁，大大提高了并发性能。每个事务根据快照读取自己可见的版本。"
    elif '两段锁' in lower_content:
        return "两段锁协议将事务分为扩展阶段和收缩阶段。扩展阶段只能申请锁，不能释放锁；收缩阶段只能释放锁，不能申请锁。遵循两段锁协议的事务一定是可串行化的。"
    elif '锁的类型' in lower_content or '共享锁' in lower_content or '排他锁' in lower_content:
        return "共享锁（S锁）允许多个事务同时读取同一数据，排他锁（X锁）只允许一个事务对数据进行读写操作。锁的兼容性决定了事务之间是否可以同时持有同一数据的锁。"
    elif '并发操作' in lower_content or '脏读' in lower_content:
        return "并发操作可能导致脏读、不可重复读和幻读等问题。脏读是读取了未提交的数据，不可重复读是同一事务内多次读取同一数据结果不一致，幻读是同一事务内两次查询同一条件返回行数不同。"
    elif '事务隔离' in lower_content:
        return "事务隔离级别从低到高依次是读未提交、读已提交、可重复读和串行化。隔离级别越高，并发性能越低，但数据一致性越好。"
    elif 'acid' in lower_content:
        return "ACID是事务的四大特性：原子性保证事务要么全部执行要么全部回滚；一致性保证事务执行前后数据保持有效状态；隔离性保证事务之间相互隔离；持久性保证事务提交后数据永久保存。"
    elif '数据库系统' in lower_content:
        return "数据库系统由数据库、数据库管理系统、应用程序和数据库管理员组成。数据库是长期存储的有组织的数据集合，DBMS是管理和维护数据库的核心软件。"
    elif '数据模型' in lower_content:
        return "数据模型分为概念模型、逻辑模型和物理模型。概念模型（如ER模型）描述现实世界，逻辑模型（如关系模型）描述数据的逻辑结构，物理模型描述数据的存储方式。"
    elif '安全性' in lower_content:
        return "数据库安全性通过用户标识鉴别、存取控制、视图机制、审计和数据加密等多种手段来保护数据库，防止数据泄露、更改或破坏。"
    elif '完整性' in lower_content:
        return "数据库完整性包括实体完整性（主键非空且唯一）、参照完整性（外键约束）和用户定义完整性（自定义约束）。完整性约束保证数据的正确性和相容性。"
    elif 'sql' in lower_content:
        return "SQL语言包括数据定义语言（DDL）、数据操纵语言（DML）、数据查询语言（DQL）和数据控制语言（DCL）。DDL用于定义数据库结构，DML用于操纵数据，DQL用于查询数据，DCL用于控制权限。"
    elif '恢复' in lower_content:
        return "数据库恢复技术通过日志文件、检查点和数据库转储来实现。事务故障通过UNDO恢复，系统故障通过UNDO+REDO恢复，介质故障需要重装数据库并REDO所有已提交事务。"
    elif '数据依赖' in lower_content or '函数依赖' in lower_content:
        return "数据依赖包括函数依赖、多值依赖和连接依赖。函数依赖是最基本的依赖关系，规范化过程就是逐步消除不合适的数据依赖，提高数据质量。"
    elif '范式' in lower_content:
        return "范式从低到高依次是1NF、2NF、3NF、BCNF、4NF、5NF。1NF要求属性原子化，2NF消除部分函数依赖，3NF消除传递函数依赖，BCNF消除主属性依赖。"
    elif '索引' in lower_content:
        return "索引分为聚集索引和非聚集索引。聚集索引按索引键顺序存储数据，非聚集索引叶子节点存储主键。覆盖索引包含所有查询字段，无需回表查询。"
    elif '事务状态' in lower_content:
        return "事务经历活动状态、部分提交状态、失败状态、中止状态和提交状态。事务的状态转换反映了事务的执行过程和结果。"
    else:
        if mermaid_result:
            return f"本图展示了{mermaid_result.get('title', content)}的核心结构和关键组件之间的关系。通过可视化图表，可以清晰理解该知识点的整体架构和组成要素。"
        return f"{content}是数据库系统中的重要概念，涉及多个核心要素和它们之间的相互关系。"


@router.post("/generate-media")
def generate_media(request: dict, db: Session = Depends(get_db)):
    knowledge_point_id = request.get("knowledge_point_id")
    question_text = request.get("question_text", "")
    
    if not knowledge_point_id:
        return {"error": "必须提供知识点ID"}
    
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == knowledge_point_id).first()
    if not kp:
        return {"error": "未找到对应的知识点"}
    
    lower_question = question_text.lower()
    
    if any(word in lower_question for word in ["画", "画一下", "绘制", "图解", "示意图", "以图片的形式展示", "图片展示", "图片形式", "生成图片", "图片总结"]):
        mermaid_result = generate_mermaid_script_simple(kp, question_text)
        if mermaid_result:
            return mermaid_result
        return generate_image_url(kp, question_text)
    
    if any(word in lower_question for word in ["演示", "动画", "过程", "步骤", "执行", "视频"]):
        return generate_animation_script(kp)
    
    return {"error": "未知的媒体类型"}
