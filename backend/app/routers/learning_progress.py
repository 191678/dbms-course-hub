from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models import LearningRecord, KnowledgePoint, MODULE_TYPES
from app.schemas import (
    LearningRecordCreate,
    LearningRecordUpdate,
    LearningRecordResponse,
    LearningRecordBatchCreate,
    LearningProgressSummary,
    LearningRecordQuery
)

router = APIRouter(tags=["learning_progress"])


@router.post("/records/", response_model=LearningRecordResponse)
def create_learning_record(record: LearningRecordCreate, db: Session = Depends(get_db)):
    existing = db.query(LearningRecord).filter(
        LearningRecord.session_id == record.session_id,
        LearningRecord.module_type == record.module_type,
        LearningRecord.module_id == (record.module_id or "")
    ).first()

    if existing:
        last_duration = existing.last_recorded_duration or 0
        current_total = record.duration_seconds or 0
        new_duration = max(0, current_total - last_duration)
        
        existing.duration_seconds = (existing.duration_seconds or 0) + new_duration
        existing.study_duration_minutes = record.study_duration_minutes or existing.study_duration_minutes
        existing.status = record.status or existing.status
        existing.interaction_count = (existing.interaction_count or 0) + (record.interaction_count or 0)
        existing.last_recorded_duration = current_total
        
        if record.module_name:
            existing.module_name = record.module_name
        if record.completion_percentage is not None:
            existing.completion_percentage = max(existing.completion_percentage or 0, record.completion_percentage)
        if record.last_study_time:
            try:
                existing.last_study_time = datetime.fromisoformat(record.last_study_time.replace('Z', '+00:00'))
            except:
                existing.last_study_time = datetime.utcnow()
        if record.mastered_count:
            existing.mastered_count = max(existing.mastered_count or 0, record.mastered_count)
        if record.not_mastered_count:
            existing.not_mastered_count = max(existing.not_mastered_count or 0, record.not_mastered_count)
        
        existing.updated_at = datetime.utcnow()
        
        if record.extra_data:
            existing.extra_data = record.extra_data
        
        db.commit()
        db.refresh(existing)
        return _serialize_record(existing)
    
    new_record = LearningRecord(
        record_uuid=str(uuid.uuid4()),
        session_id=record.session_id,
        student_id=record.student_id,
        module_type=record.module_type,
        module_id=record.module_id,
        module_name=record.module_name,
        knowledge_point_id=record.knowledge_point_id,
        knowledge_point_content=record.knowledge_point_content,
        duration_seconds=record.duration_seconds,
        study_duration_minutes=record.study_duration_minutes,
        status=record.status,
        completion_percentage=record.completion_percentage,
        interaction_count=record.interaction_count,
        last_recorded_duration=record.duration_seconds,
        last_study_time=datetime.utcnow(),
        mastered_count=record.mastered_count,
        not_mastered_count=record.not_mastered_count,
        extra_data=record.extra_data
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return _serialize_record(new_record)


def _serialize_record(record: LearningRecord) -> dict:
    return {
        "id": record.id,
        "record_uuid": record.record_uuid,
        "session_id": record.session_id,
        "student_id": record.student_id,
        "user_id": record.user_id,
        "module_type": record.module_type,
        "module_id": record.module_id,
        "module_name": record.module_name,
        "knowledge_point_id": record.knowledge_point_id,
        "knowledge_point_content": record.knowledge_point_content,
        "duration_seconds": record.duration_seconds,
        "study_duration_minutes": record.study_duration_minutes,
        "status": record.status,
        "completion_percentage": record.completion_percentage,
        "interaction_count": record.interaction_count,
        "last_recorded_duration": record.last_recorded_duration,
        "last_study_time": record.last_study_time.isoformat() if record.last_study_time else None,
        "mastered_count": record.mastered_count,
        "not_mastered_count": record.not_mastered_count,
        "extra_data": record.extra_data,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }


@router.post("/records/batch/", response_model=List[LearningRecordResponse])
def create_batch_learning_records(batch: LearningRecordBatchCreate, db: Session = Depends(get_db)):
    results = []
    for record_data in batch.records:
        record_create = LearningRecordCreate(**record_data.model_dump())
        result = create_learning_record(record_create, db)
        results.append(result)
    return results


@router.get("/records/", response_model=List[LearningRecordResponse])
def get_learning_records(
    student_id: Optional[str] = None,
    module_type: Optional[str] = None,
    knowledge_point_id: Optional[int] = None,
    session_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(LearningRecord)
    
    if student_id:
        query = query.filter(LearningRecord.student_id == student_id)
    if module_type:
        query = query.filter(LearningRecord.module_type == module_type)
    if knowledge_point_id:
        query = query.filter(LearningRecord.knowledge_point_id == knowledge_point_id)
    if session_id:
        query = query.filter(LearningRecord.session_id == session_id)
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(LearningRecord.created_at >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(LearningRecord.created_at <= end_dt)
        except ValueError:
            pass
    
    records = query.order_by(LearningRecord.created_at.desc()).offset(offset).limit(limit).all()
    return [_serialize_record(r) for r in records]


@router.get("/summary/", response_model=LearningProgressSummary)
def get_learning_progress_summary(
    student_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LearningRecord)
    
    if student_id:
        query = query.filter(LearningRecord.student_id == student_id)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(LearningRecord.created_at >= start_dt)
        except ValueError:
            pass
    else:
        start_dt = datetime.utcnow() - timedelta(days=30)
        query = query.filter(LearningRecord.created_at >= start_dt)
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(LearningRecord.created_at <= end_dt)
        except ValueError:
            pass
    
    records = query.all()
    
    total_duration = sum(r.duration_seconds or 0 for r in records)
    total_study_minutes = sum(r.study_duration_minutes or 0 for r in records)
    total_records = len(records)
    
    modules_visited = list(set(r.module_type for r in records))
    
    kp_stats = {}
    for r in records:
        if r.knowledge_point_content:
            content = r.knowledge_point_content
            if content not in kp_stats:
                kp_stats[content] = {
                    "knowledge_point": content,
                    "total_duration": 0,
                    "visit_count": 0,
                    "modules": set()
                }
            kp_stats[content]["total_duration"] += r.duration_seconds or 0
            kp_stats[content]["visit_count"] += 1
            kp_stats[content]["modules"].add(r.module_type)
    
    knowledge_points_learned = []
    for stats in kp_stats.values():
        knowledge_points_learned.append({
            "knowledge_point": stats["knowledge_point"],
            "total_duration": stats["total_duration"],
            "visit_count": stats["visit_count"],
            "modules": list(stats["modules"])
        })
    
    module_stats = {}
    for r in records:
        module_name = MODULE_TYPES.get(r.module_type, r.module_type)
        if module_name not in module_stats:
            module_stats[module_name] = {
                "module_type": r.module_type,
                "module_name": module_name,
                "total_duration": 0,
                "visit_count": 0,
                "interaction_count": 0
            }
        module_stats[module_name]["total_duration"] += r.duration_seconds or 0
        module_stats[module_name]["visit_count"] += 1
        module_stats[module_name]["interaction_count"] += r.interaction_count or 0
    
    completion_percentages = [r.completion_percentage for r in records if r.completion_percentage > 0]
    overall_completion = sum(completion_percentages) / len(completion_percentages) if completion_percentages else 0.0
    
    return LearningProgressSummary(
        total_duration_seconds=total_duration,
        total_study_minutes=total_study_minutes,
        total_records=total_records,
        modules_visited=modules_visited,
        knowledge_points_learned=knowledge_points_learned,
        module_statistics=module_stats,
        overall_completion_percentage=round(overall_completion, 2)
    )


@router.put("/records/{record_id}", response_model=LearningRecordResponse)
def update_learning_record(
    record_id: int,
    update: LearningRecordUpdate,
    db: Session = Depends(get_db)
):
    record = db.query(LearningRecord).filter(LearningRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="学习记录不存在")
    
    update_data = update.model_dump(exclude_unset=True)
    if "duration_seconds" in update_data:
        last_duration = record.last_recorded_duration or 0
        current_total = update_data["duration_seconds"]
        new_duration = max(0, current_total - last_duration)
        record.duration_seconds = (record.duration_seconds or 0) + new_duration
        record.last_recorded_duration = current_total
        del update_data["duration_seconds"]
    
    if "last_study_time" in update_data:
        try:
            record.last_study_time = datetime.fromisoformat(update_data["last_study_time"].replace('Z', '+00:00'))
        except:
            record.last_study_time = datetime.utcnow()
        del update_data["last_study_time"]
    
    for key, value in update_data.items():
        if hasattr(record, key):
            setattr(record, key, value)
    
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return _serialize_record(record)


@router.delete("/records/{record_id}")
def delete_learning_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(LearningRecord).filter(LearningRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="学习记录不存在")
    
    db.delete(record)
    db.commit()
    return {"success": True, "message": "学习记录已删除"}


@router.delete("/records/session/{session_id}")
def delete_session_records(session_id: str, db: Session = Depends(get_db)):
    records = db.query(LearningRecord).filter(LearningRecord.session_id == session_id).all()
    if not records:
        raise HTTPException(status_code=404, detail="未找到该会话的学习记录")
    
    for record in records:
        db.delete(record)
    db.commit()
    return {"success": True, "message": f"已删除 {len(records)} 条学习记录"}


@router.get("/module-types/")
def get_module_types():
    return {
        "success": True,
        "module_types": MODULE_TYPES,
        "status_types": {
            "viewing": "浏览中",
            "completed": "已完成",
            "in_progress": "进行中",
            "paused": "已暂停"
        }
    }


@router.post("/session/start")
def start_session(student_id: str = "anonymous", db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    
    session_record = LearningRecord(
        session_id=session_id,
        student_id=student_id,
        module_type="session_start",
        module_id=None,
        duration_seconds=0,
        status="started",
        interaction_count=0,
        last_recorded_duration=0,
        extra_data={"event": "session_start", "timestamp": datetime.utcnow().isoformat()}
    )
    db.add(session_record)
    db.commit()
    
    return {
        "success": True,
        "session_id": session_id,
        "message": "会话已创建",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/session/end/{session_id}")
def end_session(session_id: str, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    
    records = db.query(LearningRecord).filter(LearningRecord.session_id == session_id).all()
    if not records:
        return {"success": True, "message": "会话无记录", "total_duration": 0}
    
    total_duration = sum(r.duration_seconds or 0 for r in records)
    
    return {
        "success": True,
        "message": "会话已结束",
        "session_id": session_id,
        "total_duration_seconds": total_duration,
        "total_records": len(records),
        "timestamp": now.isoformat()
    }
