"""智能助教视频生成回归测试。

覆盖：
1. 全部知识点逐个生成视频（页数/时长/标题一致性，防止张冠李戴）
2. 具体子知识点提问（实体完整性/参照完整性/用户定义完整性）
3. SQL 单语句提问（delete/insert/select）
4. 知识点缺失时的关键词兜底（B+树）
5. 无法匹配时的明确错误提示
6. 非视频提问（兼容性回归）

运行：python test_video_generation.py
"""
import sys
import time

sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import KnowledgePoint, AgentChatHistory
from app.routers.agent import chat
from app.schemas import ChatRequest
from app.agent.tools import generate_video_presentation

TEST_STUDENT = 'TEST_VIDEO_0001'
SLIDES_COUNT = 20
DURATION = '300秒'

results = []


def check(name, condition, detail=''):
    results.append((name, bool(condition), detail))
    print(('PASS' if condition else 'FAIL'), '|', name, ('| ' + detail if detail else ''))


def ask(question):
    """走真实的 /agent/chat 处理链路。"""
    db = SessionLocal()
    try:
        start = time.time()
        resp = chat(ChatRequest(student_question=question, student_id=TEST_STUDENT, context={}), db)
        elapsed = time.time() - start
        return resp, elapsed
    finally:
        db.close()


def media_of(resp):
    return getattr(resp, 'media_data', None)


def title_of(resp):
    media = media_of(resp)
    return (getattr(media, 'title', '') or '') if media else ''


def slides_of(resp):
    media = media_of(resp)
    return (getattr(media, 'slides', None) or []) if media else []


def answer_of(resp):
    return getattr(resp, 'answer', '') or ''


def cleanup_history():
    db = SessionLocal()
    try:
        db.query(AgentChatHistory).filter(AgentChatHistory.student_id == TEST_STUDENT).delete(
            synchronize_session=False
        )
        db.commit()
    finally:
        db.close()


def test_all_knowledge_points():
    """每个知识点都必须生成与其标题一致的 20 页/300 秒视频。"""
    db = SessionLocal()
    try:
        kps = db.query(KnowledgePoint).order_by(KnowledgePoint.id).all()
    finally:
        db.close()

    for kp in kps:
        video = generate_video_presentation(kp, kp.content)
        ok = (
            video['title'] == kp.content
            and video['slides_count'] == SLIDES_COUNT
            and video['duration'] == DURATION
            and len(video['slides']) == SLIDES_COUNT
        )
        check(f'知识点{kp.id} {kp.content}', ok, video['slides'][0]['title'])

        # 完整性类知识点不能出现 ER 模型幻灯片
        if '完整性' in (kp.content or ''):
            er_hit = any('ER模型' in s['title'] for s in video['slides'])
            check(f'知识点{kp.id} 不含ER模板', not er_hit)


def test_subtopics():
    cases = [
        ('演示实体完整性', '实体完整性'),
        ('演示参照完整性', '参照完整性'),
        ('演示用户定义完整性', '用户定义完整性'),
    ]
    for question, expected in cases:
        resp, elapsed = ask(question)
        slides = slides_of(resp)
        first_titles = ' '.join(s.get('title', '') for s in slides[:3])
        ok = (
            title_of(resp).find(expected) >= 0
            and expected in first_titles
            and len(slides) == SLIDES_COUNT
            and elapsed < 3.0
        )
        slide1 = slides[0]['title'] if slides else None
        check(f'子知识点 {question}', ok, f'title={title_of(resp)} slide1={slide1} 耗时={elapsed:.2f}s')
        # 必须不串到其它约束类型或 ER 模型
        wrong = [s.get('title', '') for s in slides if 'ER模型' in s.get('title', '')]
        check(f'子知识点 {question} 不串模板', not wrong)


def test_sql_statements():
    cases = [
        ('演示delete语句', 'DELETE'),
        ('演示insert语句', 'INSERT'),
        ('演示select语句', 'SELECT'),
    ]
    for question, expected in cases:
        resp, elapsed = ask(question)
        slides = slides_of(resp)
        ok = expected in title_of(resp) and len(slides) == SLIDES_COUNT
        check(f'SQL语句 {question}', ok, f'title={title_of(resp)} 耗时={elapsed:.2f}s')

        # 只讲该语句，不能包含其它语句的小节
        other = {'DELETE': 'INSERT', 'INSERT': 'DELETE', 'SELECT': 'DELETE'}[expected]
        texts = ' '.join((s.get('title', '') + s.get('content', '')) for s in slides)
        check(f'SQL语句 {question} 不混入其它语句', other not in texts)


def test_keyword_fallback():
    resp, elapsed = ask('演示B+树的删除操作')
    title = title_of(resp)
    check('B+树关键词兜底', 'B+树' in title, f'title={title}')
    check('B+树不生成DELETE语句视频', 'DELETE' not in title, f'耗时={elapsed:.2f}s')


def test_no_match():
    resp, _ = ask('演示量子计算')
    answer = answer_of(resp)
    check('无法匹配时给出明确提示', media_of(resp) is None and ('未找到' in answer or '抱歉' in answer), answer[:60])


def test_non_video_regression():
    """非视频提问必须仍走文本讲解，不受视频链路修复影响。"""
    resp, _ = ask('什么是ACID')
    answer = answer_of(resp)
    check('非视频提问文本讲解正常', media_of(resp) is None and len(answer) > 100, f'len={len(answer)}')

    resp, _ = ask('什么是死锁')
    answer = answer_of(resp)
    check('死锁文本讲解正常', media_of(resp) is None and '死锁' in answer)


if __name__ == '__main__':
    print('===== 视频生成功能测试 =====')
    test_all_knowledge_points()
    test_subtopics()
    test_sql_statements()
    test_keyword_fallback()
    test_no_match()
    test_non_video_regression()
    cleanup_history()

    failed = [r for r in results if not r[1]]
    print('\n===== 汇总 =====')
    print(f'用例 {len(results)} 个，通过 {len(results) - len(failed)} 个，失败 {len(failed)} 个')
    for name, _ok, detail in failed:
        print('FAILED:', name, detail)
    sys.exit(1 if failed else 0)
