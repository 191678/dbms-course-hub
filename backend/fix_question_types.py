"""Fix question type values to use Chinese names matching frontend."""
from app.database import get_db
from app.models import Question

db = next(get_db())

# Map English types to Chinese
type_mapping = {
    'single': '单选',
    'multi': '多选',
    'judge': '判断',
    'SQL编程': 'SQL编程'
}

# Update question types
for eng_type, cn_type in type_mapping.items():
    if eng_type == cn_type:
        continue
    count = db.query(Question).filter(Question.type == eng_type).update({'type': cn_type})
    print(f"Updated {count} questions from '{eng_type}' to '{cn_type}'")

db.commit()

# Verify
types = db.query(Question.type).distinct().all()
print(f"\nQuestion types in DB: {[t[0] for t in types]}")

counts = db.query(Question.type, db.query(Question).filter(Question.type == Question.type).count()).group_by(Question.type).all()
for qtype, count in counts:
    print(f"  {qtype}: {count}")
