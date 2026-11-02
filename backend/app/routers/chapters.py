from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Chapter, KnowledgePoint
from app.schemas import ChapterCreate, ChapterUpdate, ChapterResponse, KnowledgePointResponse

router = APIRouter()


def build_knowledge_point_tree(kps):
    kp_map = {kp.id: kp for kp in kps}
    root_kps = []
    
    for kp in kps:
        if kp.parent_id is None:
            root_kps.append(kp)
        elif kp.parent_id in kp_map:
            kp_map[kp.parent_id].children.append(kp)
    
    return sorted(root_kps, key=lambda x: x.order_index)


@router.get("/", response_model=list[ChapterResponse])
def get_chapters(
    db: Session = Depends(get_db),
    category: str = Query(None, description="按分类筛选知识点")
):
    chapters = db.query(Chapter).options(
        joinedload(Chapter.knowledge_points).joinedload(KnowledgePoint.questions)
    ).order_by(Chapter.order_index).all()
    
    for chapter in chapters:
        if category:
            chapter.knowledge_points = [
                kp for kp in chapter.knowledge_points 
                if kp.category == category
            ]
        
        chapter.knowledge_points = build_knowledge_point_tree(chapter.knowledge_points)
    
    return chapters


@router.get("/{chapter_id}/", response_model=ChapterResponse)
def get_chapter(
    chapter_id: int, 
    db: Session = Depends(get_db),
    category: str = Query(None, description="按分类筛选知识点")
):
    chapter = db.query(Chapter).options(
        joinedload(Chapter.knowledge_points).joinedload(KnowledgePoint.questions)
    ).filter(Chapter.id == chapter_id).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if category:
        chapter.knowledge_points = [
            kp for kp in chapter.knowledge_points 
            if kp.category == category
        ]
    
    chapter.knowledge_points = build_knowledge_point_tree(chapter.knowledge_points)
    
    return chapter


@router.get("/{chapter_id}/categories/")
def get_chapter_categories(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    categories = db.query(KnowledgePoint.category).distinct().filter(
        KnowledgePoint.chapter_id == chapter_id
    ).all()
    
    return {"categories": [cat[0] for cat in categories if cat[0]]}


@router.post("/", response_model=ChapterResponse)
def create_chapter(chapter: ChapterCreate, db: Session = Depends(get_db)):
    db_chapter = Chapter(
        title=chapter.title,
        description=chapter.description,
        order_index=chapter.order_index
    )
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


@router.put("/{chapter_id}/", response_model=ChapterResponse)
def update_chapter(chapter_id: int, chapter: ChapterUpdate, db: Session = Depends(get_db)):
    db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not db_chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if chapter.title is not None:
        db_chapter.title = chapter.title
    if chapter.description is not None:
        db_chapter.description = chapter.description
    if chapter.order_index is not None:
        db_chapter.order_index = chapter.order_index
    
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


@router.delete("/{chapter_id}/")
def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    db.delete(chapter)
    db.commit()
    return {"message": "Chapter deleted successfully"}
