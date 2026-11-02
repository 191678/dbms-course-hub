# -*- coding: utf-8 -*-
"""验证所有知识点内容完整性"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import KnowledgePoint

db = SessionLocal()
kps = db.query(KnowledgePoint).order_by(KnowledgePoint.id).all()

print(f"总知识点数: {len(kps)}")
print("ID  原理字数  要点数  步骤数  注意数  FAQ数  状态")
print("-" * 55)

all_ok = True
for kp in kps:
    detail_len = len(kp.detail_content) if kp.detail_content else 0
    kp_count = len(kp.key_points) if kp.key_points else 0
    step_count = len(kp.learning_steps) if kp.learning_steps else 0
    tip_count = len(kp.tips) if kp.tips else 0
    faq_count = len(kp.faq) if kp.faq else 0
    
    ok = detail_len >= 200 and kp_count >= 4 and step_count >= 4 and tip_count >= 3 and faq_count >= 3
    if not ok:
        all_ok = False
    status = "PASS" if ok else "FAIL"
    print(f"{kp.id:>3}  {detail_len:>6}    {kp_count:>4}    {step_count:>4}    {tip_count:>4}    {faq_count:>4}    {status}")

print("-" * 55)
print(f"全部通过: {all_ok}")
db.close()
