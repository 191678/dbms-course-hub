"""Verify question data is correct."""
from app.database import get_db
from app.models import Question, Chapter, KnowledgePoint
import json

db = next(get_db())

# Check question types properly
from sqlalchemy import func
counts = db.query(Question.type, func.count(Question.id)).group_by(Question.type).all()
print("Question type distribution:")
for qtype, count in counts:
    print(f"  {qtype}: {count}")

# Check first question
q = db.query(Question).first()
if q:
    print(f"\nSample question:")
    print(f"  ID: {q.id}")
    print(f"  Type: {q.type}")
    print(f"  Stem: {q.stem[:50]}")
    print(f"  Options: {q.options} (type: {type(q.options).__name__})")
    print(f"  Answer: {q.answer}")
    print(f"  Analysis: {q.analysis[:50] if q.analysis else 'None'}")

# Check chapters with knowledge points
chapters = db.query(Chapter).order_by(Chapter.id).all()
print(f"\nChapters: {len(chapters)}")
for ch in chapters[:3]:
    kps_count = db.query(KnowledgePoint).filter(KnowledgePoint.chapter_id == ch.id).count()
    q_count = db.query(Question).join(KnowledgePoint).filter(KnowledgePoint.chapter_id == ch.id).count()
    print(f"  Ch {ch.id}: {ch.title} ({kps_count} KPs, {q_count} questions)")
