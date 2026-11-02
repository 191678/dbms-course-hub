"""Fix question options - ensure they are stored as proper Python lists in JSON column."""
from app.database import get_db
from app.models import Question
import json

db = next(get_db())

questions = db.query(Question).all()
fixed = 0
for q in questions:
    if q.options and isinstance(q.options, str):
        try:
            parsed = json.loads(q.options)
            q.options = parsed
            fixed += 1
        except (json.JSONDecodeError, TypeError):
            pass
    elif q.options is None:
        pass
    # If it's already a list/dict, leave it alone

db.commit()
print(f"Fixed {fixed} questions with string options")

# Verify
q = db.query(Question).first()
if q:
    print(f"\nSample options: {q.options} (type: {type(q.options).__name__})")
