from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import KnowledgePoint
from app.schemas import KnowledgePointCreate, KnowledgePointUpdate, KnowledgePointResponse

router = APIRouter()


@router.get("/", response_model=list[KnowledgePointResponse])
def get_knowledge_points(
    chapter_id: int = None,
    difficulty: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(KnowledgePoint)
    
    if chapter_id:
        query = query.filter(KnowledgePoint.chapter_id == chapter_id)
    if difficulty:
        query = query.filter(KnowledgePoint.difficulty == difficulty)
    
    return query.order_by(KnowledgePoint.id).all()


@router.get("/{knowledge_point_id}/", response_model=KnowledgePointResponse)
def get_knowledge_point(knowledge_point_id: int, db: Session = Depends(get_db)):
    knowledge_point = db.query(KnowledgePoint).filter(KnowledgePoint.id == knowledge_point_id).first()
    if not knowledge_point:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    return knowledge_point


@router.post("/", response_model=KnowledgePointResponse)
def create_knowledge_point(knowledge_point: KnowledgePointCreate, db: Session = Depends(get_db)):
    db_knowledge_point = KnowledgePoint(
        chapter_id=knowledge_point.chapter_id,
        content=knowledge_point.content,
        difficulty=knowledge_point.difficulty
    )
    db.add(db_knowledge_point)
    db.commit()
    db.refresh(db_knowledge_point)
    return db_knowledge_point


@router.put("/{knowledge_point_id}/", response_model=KnowledgePointResponse)
def update_knowledge_point(knowledge_point_id: int, knowledge_point: KnowledgePointUpdate, db: Session = Depends(get_db)):
    db_knowledge_point = db.query(KnowledgePoint).filter(KnowledgePoint.id == knowledge_point_id).first()
    if not db_knowledge_point:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    
    if knowledge_point.content is not None:
        db_knowledge_point.content = knowledge_point.content
    if knowledge_point.difficulty is not None:
        db_knowledge_point.difficulty = knowledge_point.difficulty
    
    db.commit()
    db.refresh(db_knowledge_point)
    return db_knowledge_point


@router.delete("/{knowledge_point_id}/")
def delete_knowledge_point(knowledge_point_id: int, db: Session = Depends(get_db)):
    knowledge_point = db.query(KnowledgePoint).filter(KnowledgePoint.id == knowledge_point_id).first()
    if not knowledge_point:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    
    db.delete(knowledge_point)
    db.commit()
    return {"message": "Knowledge point deleted successfully"}
