# -*- coding: utf-8 -*-
"""
全面扩充知识点内容 - 主执行脚本
合并所有章节的扩充内容，更新到数据库
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import KnowledgePoint
from comprehensive_enrich_part1 import ENRICHMENTS as E1
from comprehensive_enrich_part2 import ENRICHMENTS as E2
from comprehensive_enrich_part3 import ENRICHMENTS as E3
from comprehensive_enrich_part4 import ENRICHMENTS as E4
from comprehensive_enrich_part5 import ENRICHMENTS as E5

# 合并所有章节的内容
ALL_ENRICHMENTS = {}
ALL_ENRICHMENTS.update(E1)
ALL_ENRICHMENTS.update(E2)
ALL_ENRICHMENTS.update(E3)
ALL_ENRICHMENTS.update(E4)
ALL_ENRICHMENTS.update(E5)

print(f"共加载 {len(ALL_ENRICHMENTS)} 个知识点的扩充内容")

db = SessionLocal()

updated_count = 0
for kp_id, data in ALL_ENRICHMENTS.items():
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
    if kp:
        kp.detail_content = data["detail_content"]
        kp.key_points = data["key_points"]
        kp.learning_steps = data["learning_steps"]
        kp.tips = data["tips"]
        kp.faq = data["faq"]
        updated_count += 1
        print(f"  ✓ 已更新知识点 {kp_id}: {kp.content[:30]}...")

db.commit()
db.close()

print(f"\n完成！共更新 {updated_count} 个知识点")
