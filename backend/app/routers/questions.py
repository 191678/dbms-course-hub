from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Question
from app.schemas import QuestionCreate, QuestionUpdate, QuestionResponse
from typing import List, Optional

router = APIRouter()


@router.get("/", response_model=list[QuestionResponse])
def get_questions(
    knowledge_point_id: Optional[int] = None,
    type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=2000),
    db: Session = Depends(get_db)
):
    query = db.query(Question)
    
    if knowledge_point_id:
        query = query.filter(Question.knowledge_point_id == knowledge_point_id)
    if type:
        query = query.filter(Question.type == type)
    
    return query.limit(limit).all()


@router.get("/{question_id}/", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.post("/", response_model=QuestionResponse)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    db_question = Question(
        knowledge_point_id=question.knowledge_point_id,
        type=question.type,
        stem=question.stem,
        options=question.options,
        answer=question.answer,
        analysis=question.analysis
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


@router.put("/{question_id}/", response_model=QuestionResponse)
def update_question(question_id: int, question: QuestionUpdate, db: Session = Depends(get_db)):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if question.type is not None:
        db_question.type = question.type
    if question.stem is not None:
        db_question.stem = question.stem
    if question.options is not None:
        db_question.options = question.options
    if question.answer is not None:
        db_question.answer = question.answer
    if question.analysis is not None:
        db_question.analysis = question.analysis
    
    db.commit()
    db.refresh(db_question)
    return db_question


@router.delete("/{question_id}/")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully"}


@router.post("/batch/")
def create_questions(questions: List[QuestionCreate], db: Session = Depends(get_db)):
    db_questions = [
        Question(
            knowledge_point_id=q.knowledge_point_id,
            type=q.type,
            stem=q.stem,
            options=q.options,
            answer=q.answer,
            analysis=q.analysis
        )
        for q in questions
    ]
    db.add_all(db_questions)
    db.commit()
    return {"message": f"Created {len(db_questions)} questions successfully"}
