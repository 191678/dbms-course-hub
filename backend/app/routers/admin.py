from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
from datetime import datetime, date, timedelta
from collections import defaultdict
import json

from app.database import get_db
from app.models import (
    StudentUser, StudyRecord, StudyStatistics, LearningRecord,
    KnowledgePointTag, StudentKnowledgePoint, KnowledgePointTagRelation,
    CourseContent, CourseContentVersion, QuestionUsage, VisualizationTemplate,
    Role, Permission, UserRole, RolePermission,
    Question, KnowledgePoint, Chapter, MODULE_TYPES
)
from app.schemas_admin import (
    RoleCreate, RoleUpdate, RoleResponse,
    PermissionCreate, PermissionResponse,
    UserRoleCreate, UserRoleResponse,
    StudyRecordCreate, StudyRecordUpdate, StudyRecordResponse,
    StudyStatisticsResponse, BatchImportRequest,
    TagCreate, TagUpdate, TagResponse,
    StudentKPCreate, StudentKPUpdate, StudentKPResponse,
    KPTagRelationCreate,
    CourseContentCreate, CourseContentUpdate, CourseContentResponse,
    ContentVersionResponse, ContentPublishRequest,
    QuestionBatchImport, QuestionExportRequest, QuestionUsageResponse,
    VizTemplateCreate, VizTemplateUpdate, VizTemplateResponse
)
from app.schemas import QuestionCreate, QuestionUpdate, QuestionResponse
from app.utils.permissions import require_admin, require_permission, init_rbac_data
from app.utils.auth import hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ==================== 仪表盘 ====================

@router.get("/")
def admin_dashboard(db: Session = Depends(get_db), admin=Depends(require_admin)):
    student_count = db.query(StudentUser).filter(StudentUser.role == "student", StudentUser.is_active == True).count()
    admin_count = db.query(StudentUser).filter(StudentUser.role.in_(["admin", "teacher"]), StudentUser.is_active == True).count()
    chapters_count = db.query(Chapter).count()
    kp_count = db.query(KnowledgePoint).count()
    question_count = db.query(Question).count()
    content_count = db.query(CourseContent).count()
    study_records_count = db.query(StudyRecord).count()
    today_minutes = db.query(func.coalesce(func.sum(StudyRecord.duration_minutes), 0)).filter(
        func.date(StudyRecord.study_date) == date.today()
    ).scalar()
    abnormal_count = db.query(StudyRecord).filter(StudyRecord.is_abnormal == True).count()
    mastered_kps = db.query(StudentKnowledgePoint).filter(StudentKnowledgePoint.mastery_level == "mastered").count()
    total_kp_students = db.query(StudentKnowledgePoint).count()

    # ---- 图表数据（用于仪表盘可视化）----
    # 1) 饼图：知识点掌握度分布
    mastery_label = {"mastered": "已掌握", "learning": "学习中", "practicing": "学习中", "not_started": "未开始", "unknown": "未开始"}
    mastery_pie = [
        {"name": mastery_label.get(level or "unknown", level or "未开始"), "value": int(cnt)}
        for level, cnt in db.query(StudentKnowledgePoint.mastery_level, func.count(StudentKnowledgePoint.id))
        .group_by(StudentKnowledgePoint.mastery_level).all()
    ]
    if sum(item["value"] for item in mastery_pie) == 0:
        mastery_pie = [
            {"name": "正常记录", "value": max(study_records_count - abnormal_count, 0)},
            {"name": "异常记录", "value": abnormal_count},
        ]

    # 2) 折线图：近 7 天学习时长趋势
    today = date.today()
    trend_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    trend_map = {}
    for d, minutes in (
        db.query(func.date(StudyRecord.study_date), func.coalesce(func.sum(StudyRecord.duration_minutes), 0))
        .group_by(func.date(StudyRecord.study_date)).all()
    ):
        trend_map[str(d)] = int(minutes or 0)
    study_trend = {
        "dates": [d.strftime("%m-%d") for d in trend_days],
        "minutes": [trend_map.get(str(d), 0) for d in trend_days],
    }

    # 3) 柱状图：各章学习记录数
    chapters = db.query(Chapter).order_by(Chapter.order_index).all()
    kp_chapter = {kp_id: chapter_id for kp_id, chapter_id in db.query(KnowledgePoint.id, KnowledgePoint.chapter_id).all()}
    chapter_counts = defaultdict(int)
    for (kp_id,) in db.query(StudyRecord.knowledge_point_id).all():
        cid = kp_chapter.get(kp_id)
        if cid is not None:
            chapter_counts[cid] += 1
    chapter_bar = {
        "labels": [f"第{i + 1}章" for i in range(len(chapters))],
        "values": [chapter_counts.get(c.id, 0) for c in chapters],
    }

    # 4) 雷达图：平台资源分布
    resource_counts = [
        ("章节", chapters_count),
        ("知识点", kp_count),
        ("题目", question_count),
        ("课程内容", content_count),
        ("学习记录", study_records_count),
    ]
    resource_max = max((v for _, v in resource_counts), default=0) or 1
    resource_radar = {
        "indicators": [{"name": name, "max": resource_max} for name, _ in resource_counts],
        "values": [v for _, v in resource_counts],
    }

    # 5) 热力图：星期 × 学习类型 的活跃度
    weekday_labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    type_keys = ["self", "class", "review", "exam"]
    type_labels = {"self": "自习", "class": "上课", "review": "复习", "exam": "考试"}
    heat_grid = [[0] * 7 for _ in type_keys]
    for study_date, study_type in db.query(StudyRecord.study_date, StudyRecord.study_type).all():
        if study_date is None or study_type not in type_keys:
            continue
        heat_grid[type_keys.index(study_type)][study_date.weekday()] += 1
    activity_heatmap = {
        "xLabels": weekday_labels,
        "yLabels": [type_labels[k] for k in type_keys],
        "values": heat_grid,
    }

    charts = {
        "mastery_pie": mastery_pie,
        "study_trend": study_trend,
        "chapter_bar": chapter_bar,
        "resource_radar": resource_radar,
        "activity_heatmap": activity_heatmap,
    }

    # 功能使用分布：全部转换为业务语义名称，不暴露数据库字段
    feature_labels = {**MODULE_TYPES, "session_start": "学习会话开始", "study_session": "学习会话"}
    feature_counts = defaultdict(int)
    for module_type, count in (
        db.query(LearningRecord.module_type, func.count(LearningRecord.id))
        .group_by(LearningRecord.module_type).all()
    ):
        feature_counts[feature_labels.get(module_type, "其他学习功能")] += int(count)
    usage_total = sum(feature_counts.values()) or 1
    module_usage = [
        {"name": name, "value": value, "percentage": round(value * 100 / usage_total, 1)}
        for name, value in sorted(feature_counts.items(), key=lambda item: item[1], reverse=True)
    ]

    return {
        "student_count": student_count,
        "admin_count": admin_count,
        "chapters_count": chapters_count,
        "knowledge_points_count": kp_count,
        "questions_count": question_count,
        "course_contents_count": content_count,
        "study_records_count": study_records_count,
        "today_study_minutes": today_minutes or 0,
        "abnormal_records_count": abnormal_count,
        "mastered_knowledge_points_count": mastered_kps,
        "total_kp_students": total_kp_students,
        "module_usage": module_usage,
        "charts": charts,
    }


# ==================== RBAC 权限管理 ====================

@router.get("/rbac/init/")
def init_rbac(db: Session = Depends(get_db), admin=Depends(require_admin)):
    init_rbac_data(db)
    return {"success": True, "message": "RBAC data initialized"}


@router.get("/roles/")
def list_roles(db: Session = Depends(get_db), admin=Depends(require_admin)):
    roles = db.query(Role).all()
    result = []
    for r in roles:
        perms = db.query(Permission).join(RolePermission).filter(RolePermission.role_id == r.id).all()
        result.append({
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "is_system": r.is_system,
            "permissions": [{"id": p.id, "name": p.name, "codename": p.codename, "module": p.module} for p in perms],
            "user_count": len(r.user_roles),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return result


@router.post("/roles/", response_model=RoleResponse)
def create_role(data: RoleCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    existing = db.query(Role).filter(Role.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="角色名称已存在")
    role = Role(name=data.name, description=data.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.put("/roles/{role_id}/", response_model=RoleResponse)
def update_role(role_id: int, data: RoleUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role.is_system:
        raise HTTPException(status_code=400, detail="系统角色不可修改")
    if data.name and data.name != role.name:
        existing = db.query(Role).filter(Role.name == data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="角色名称已存在")
        role.name = data.name
    if data.description is not None:
        role.description = data.description
    db.commit()
    db.refresh(role)
    return role


@router.delete("/roles/{role_id}/")
def delete_role(role_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role.is_system:
        raise HTTPException(status_code=400, detail="系统角色不可删除")
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    db.query(UserRole).filter(UserRole.role_id == role_id).delete()
    db.delete(role)
    db.commit()
    return {"success": True, "message": "角色已删除"}


@router.post("/roles/{role_id}/permissions/")
def assign_permissions(role_id: int, permission_ids: List[int], db: Session = Depends(get_db), admin=Depends(require_admin)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    for pid in permission_ids:
        perm = db.query(Permission).filter(Permission.id == pid).first()
        if perm:
            db.add(RolePermission(role_id=role_id, permission_id=pid))
    db.commit()
    return {"success": True, "message": "权限已分配"}


@router.get("/permissions/")
def list_permissions(module: Optional[str] = Query(None), db: Session = Depends(get_db), admin=Depends(require_admin)):
    query = db.query(Permission)
    if module:
        query = query.filter(Permission.module == module)
    perms = query.order_by(Permission.module, Permission.codename).all()
    return [{
        "id": p.id,
        "name": p.name,
        "codename": p.codename,
        "description": p.description,
        "module": p.module,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    } for p in perms]


# ==================== 学生管理 ====================

@router.get("/students/")
def list_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    query = db.query(StudentUser)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(or_(
            StudentUser.student_id.ilike(search_pattern),
            StudentUser.username.ilike(search_pattern),
            StudentUser.name.ilike(search_pattern)
        ))
    if role:
        query = query.filter(StudentUser.role == role)
    total = query.count()
    students = query.order_by(StudentUser.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": s.id,
            "student_id": s.student_id,
            "username": s.username,
            "name": s.name,
            "role": s.role,
            "is_active": s.is_active,
            "last_login_at": s.last_login_at.isoformat() if s.last_login_at else None,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        } for s in students]
    }


@router.post("/students/")
def create_student(data: dict, db: Session = Depends(get_db), admin=Depends(require_admin)):
    sid = data.get("student_id")
    username = data.get("username")
    password = data.get("password", "123456")
    name = data.get("name", username)
    role = data.get("role", "student")
    if not sid or not username:
        raise HTTPException(status_code=400, detail="学号和用户名必填")
    existing = db.query(StudentUser).filter((StudentUser.student_id == sid) | (StudentUser.username == username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="学号或用户名已存在")
    user = StudentUser(student_id=sid, username=username, password_hash=hash_password(password), name=name, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "student_id": user.student_id, "username": user.username, "name": user.name, "role": user.role}


@router.put("/students/{student_id}/")
def update_student(student_id: int, data: dict, db: Session = Depends(get_db), admin=Depends(require_admin)):
    student = db.query(StudentUser).filter(StudentUser.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    for field in ["name", "role", "is_active"]:
        if field in data:
            setattr(student, field, data[field])
    if data.get("password"):
        student.password_hash = hash_password(data["password"])
    db.commit()
    db.refresh(student)
    return {"success": True, "message": "学生信息已更新"}


@router.delete("/students/{student_id}/")
def deactivate_student(student_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    student = db.query(StudentUser).filter(StudentUser.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    student.is_active = False
    db.commit()
    return {"success": True, "message": "学生已停用"}


@router.get("/students/{student_id}/study-summary/")
def student_study_summary(
    student_id: int,
    period: str = Query("month", pattern="^(day|week|month|semester)$"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    student = db.query(StudentUser).filter(StudentUser.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    today = date.today()
    if period == "day":
        start_date = today
    elif period == "week":
        start_date = today - timedelta(days=today.weekday())
    elif period == "month":
        start_date = today.replace(day=1)
    else:
        start_date = today - timedelta(days=150)
    records = db.query(StudyRecord).filter(
        StudyRecord.student_id == student.student_id,
        func.date(StudyRecord.study_date) >= start_date
    ).all()
    total_minutes = sum(r.duration_minutes for r in records)
    abnormal_count = sum(1 for r in records if r.is_abnormal)
    records_by_date = {}
    for r in records:
        d = r.study_date.strftime("%Y-%m-%d") if r.study_date else "unknown"
        if d not in records_by_date:
            records_by_date[d] = {"minutes": 0, "count": 0, "abnormal": 0}
        records_by_date[d]["minutes"] += r.duration_minutes
        records_by_date[d]["count"] += 1
        if r.is_abnormal:
            records_by_date[d]["abnormal"] += 1
    records_by_kp = {}
    for r in records:
        kp = r.knowledge_point_content or "未关联知识点"
        if kp not in records_by_kp:
            records_by_kp[kp] = {"minutes": 0, "count": 0}
        records_by_kp[kp]["minutes"] += r.duration_minutes
        records_by_kp[kp]["count"] += 1
    return {
        "student_id": student.student_id,
        "name": student.name,
        "period": period,
        "start_date": start_date.isoformat(),
        "total_minutes": total_minutes,
        "record_count": len(records),
        "abnormal_count": abnormal_count,
        "daily_stats": records_by_date,
        "kp_stats": records_by_kp,
    }


# ==================== 学习时间管理 ====================

@router.get("/study-records/")
def list_study_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    student_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    is_abnormal: Optional[bool] = Query(None),
    study_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    query = db.query(StudyRecord)
    if student_id:
        query = query.filter(StudyRecord.student_id == student_id)
    if start_date:
        query = query.filter(StudyRecord.study_date >= start_date)
    if end_date:
        query = query.filter(StudyRecord.study_date <= end_date)
    if is_abnormal is not None:
        query = query.filter(StudyRecord.is_abnormal == is_abnormal)
    if study_type:
        query = query.filter(StudyRecord.study_type == study_type)
    total = query.count()
    records = query.order_by(StudyRecord.study_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": r.id,
            "student_id": r.student_id,
            "course_name": r.course_name,
            "chapter_name": r.chapter_name,
            "knowledge_point_id": r.knowledge_point_id,
            "knowledge_point_content": r.knowledge_point_content,
            "study_date": r.study_date.isoformat() if r.study_date else None,
            "duration_minutes": r.duration_minutes,
            "study_type": r.study_type,
            "is_abnormal": r.is_abnormal,
            "abnormal_reason": r.abnormal_reason,
            "notes": r.notes,
            "source": r.source,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in records]
    }


@router.post("/study-records/")
def create_study_record(data: StudyRecordCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    record = StudyRecord(
        student_id=data.student_id,
        course_name=data.course_name,
        chapter_name=data.chapter_name,
        knowledge_point_id=data.knowledge_point_id,
        knowledge_point_content=data.knowledge_point_content,
        study_date=data.study_date,
        duration_minutes=data.duration_minutes,
        study_type=data.study_type or "self",
        is_abnormal=data.is_abnormal or False,
        abnormal_reason=data.abnormal_reason,
        notes=data.notes,
        source="manual"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/study-records/{record_id}/")
def update_study_record(record_id: int, data: StudyRecordUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    record = db.query(StudyRecord).filter(StudyRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="学习记录不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    record.source = "manual"
    db.commit()
    db.refresh(record)
    return record


@router.delete("/study-records/{record_id}/")
def delete_study_record(record_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    record = db.query(StudyRecord).filter(StudyRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="学习记录不存在")
    db.delete(record)
    db.commit()
    return {"success": True, "message": "记录已删除"}


@router.post("/study-records/batch/")
def batch_create_study_records(data: BatchImportRequest, db: Session = Depends(get_db), admin=Depends(require_admin)):
    created = 0
    skipped = 0
    for item in data.records:
        try:
            record = StudyRecord(
                student_id=item.student_id,
                course_name=item.course_name,
                chapter_name=item.chapter_name,
                knowledge_point_id=item.knowledge_point_id,
                knowledge_point_content=item.knowledge_point_content,
                study_date=item.study_date,
                duration_minutes=item.duration_minutes,
                study_type=item.study_type or "self",
                is_abnormal=item.is_abnormal or False,
                abnormal_reason=item.abnormal_reason,
                notes=item.notes,
                source="import"
            )
            db.add(record)
            created += 1
        except Exception:
            skipped += 1
    db.commit()
    return {"created": created, "skipped": skipped}


@router.get("/study-records/statistics/")
def study_statistics(
    start_date: str = Query(...),
    end_date: str = Query(...),
    group_by: str = Query("day", pattern="^(day|week|month)$"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    records = db.query(StudyRecord).filter(
        func.date(StudyRecord.study_date) >= start_date,
        func.date(StudyRecord.study_date) <= end_date
    ).all()
    stats = {}
    for r in records:
        if group_by == "day":
            key = r.study_date.strftime("%Y-%m-%d") if r.study_date else "unknown"
        elif group_by == "week":
            d = r.study_date or datetime.now()
            week_start = d - timedelta(days=d.weekday())
            key = week_start.strftime("%Y-%m-%d")
        else:
            key = r.study_date.strftime("%Y-%m") if r.study_date else "unknown"
        if key not in stats:
            stats[key] = {"total_minutes": 0, "record_count": 0, "abnormal_count": 0, "students": set()}
        stats[key]["total_minutes"] += r.duration_minutes
        stats[key]["record_count"] += 1
        if r.is_abnormal:
            stats[key]["abnormal_count"] += 1
        stats[key]["students"].add(r.student_id)
    for key in stats:
        stats[key]["student_count"] = len(stats[key].pop("students", set()))
    return {"start_date": start_date, "end_date": end_date, "group_by": group_by, "statistics": stats}


@router.post("/study-records/detect-anomalies/")
def detect_anomalies(
    min_minutes: int = Query(5, ge=0),
    max_minutes: int = Query(480, ge=30),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    records = db.query(StudyRecord).filter(StudyRecord.is_abnormal == False).all()
    detected = 0
    for r in records:
        is_abnormal = False
        reason = []
        if r.duration_minutes < min_minutes and r.duration_minutes > 0:
            is_abnormal = True
            reason.append(f"学习时间过短({r.duration_minutes}分钟)")
        if r.duration_minutes > max_minutes:
            is_abnormal = True
            reason.append(f"学习时间过长({r.duration_minutes}分钟)")
        if is_abnormal:
            r.is_abnormal = True
            r.abnormal_reason = "; ".join(reason)
            detected += 1
    db.commit()
    return {"detected": detected, "message": f"已检测并标记 {detected} 条异常记录"}


@router.get("/study-records/export/")
def export_study_records(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    query = db.query(StudyRecord)
    if start_date:
        query = query.filter(StudyRecord.study_date >= start_date)
    if end_date:
        query = query.filter(StudyRecord.study_date <= end_date)
    if student_id:
        query = query.filter(StudyRecord.student_id == student_id)
    records = query.order_by(StudyRecord.study_date.desc()).all()
    return {
        "exported_at": datetime.now().isoformat(),
        "total": len(records),
        "headers": ["ID", "学号", "课程", "章节", "知识点", "学习日期", "时长(分钟)", "类型", "异常", "备注"],
        "rows": [{
            "id": r.id,
            "student_id": r.student_id,
            "course_name": r.course_name or "",
            "chapter_name": r.chapter_name or "",
            "kp_content": r.knowledge_point_content or "",
            "study_date": r.study_date.isoformat() if r.study_date else "",
            "duration": r.duration_minutes,
            "type": r.study_type,
            "is_abnormal": "是" if r.is_abnormal else "否",
            "notes": r.notes or "",
        } for r in records]
    }


# ==================== 疑难知识点管理 ====================

@router.get("/kp-tags/")
def list_kp_tags(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    query = db.query(KnowledgePointTag)
    if category:
        query = query.filter(KnowledgePointTag.category == category)
    tags = query.all()
    tag_map = {t.id: t for t in tags}
    roots = [t for t in tags if t.parent_id is None]
    def build_tree(parent):
        children = [t for t in tags if t.parent_id == parent.id]
        return {
            "id": parent.id,
            "name": parent.name,
            "category": parent.category,
            "color": parent.color,
            "description": parent.description,
            "children": [build_tree(c) for c in children]
        }
    return [build_tree(r) for r in roots]


@router.post("/kp-tags/")
def create_kp_tag(data: TagCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    existing = db.query(KnowledgePointTag).filter(KnowledgePointTag.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="标签名已存在")
    tag = KnowledgePointTag(
        name=data.name,
        category=data.category or "custom",
        parent_id=data.parent_id,
        color=data.color,
        description=data.description
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.put("/kp-tags/{tag_id}/")
def update_kp_tag(tag_id: int, data: TagUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    tag = db.query(KnowledgePointTag).filter(KnowledgePointTag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tag, key, value)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/kp-tags/{tag_id}/")
def delete_kp_tag(tag_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    tag = db.query(KnowledgePointTag).filter(KnowledgePointTag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    children = db.query(KnowledgePointTag).filter(KnowledgePointTag.parent_id == tag_id).all()
    for child in children:
        child.parent_id = tag.parent_id
    rels = db.query(KnowledgePointTagRelation).filter(KnowledgePointTagRelation.tag_id == tag_id).all()
    for rel in rels:
        db.delete(rel)
    db.delete(tag)
    db.commit()
    return {"success": True, "message": "标签已删除"}


@router.get("/student-kps/")
def list_student_kps(
    student_id: Optional[str] = Query(None),
    mastery_level: Optional[str] = Query(None),
    chapter_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    query = db.query(StudentKnowledgePoint)
    if student_id:
        query = query.filter(StudentKnowledgePoint.student_id == student_id)
    if mastery_level:
        query = query.filter(StudentKnowledgePoint.mastery_level == mastery_level)
    records = query.all()
    result = []
    for r in records:
        kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == r.knowledge_point_id).first()
        tags = db.query(KnowledgePointTag).join(KnowledgePointTagRelation).filter(
            KnowledgePointTagRelation.student_kp_id == r.id
        ).all()
        result.append({
            "id": r.id,
            "student_id": r.student_id,
            "knowledge_point_id": r.knowledge_point_id,
            "kp_content": kp.content if kp else None,
            "chapter_id": kp.chapter_id if kp else None,
            "mastery_level": r.mastery_level,
            "difficulty_level": r.difficulty_level,
            "last_study_date": r.last_study_date.isoformat() if r.last_study_date else None,
            "study_count": r.study_count,
            "total_study_minutes": r.total_study_minutes,
            "note": r.note,
            "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in tags],
        })
    return result


@router.post("/student-kps/")
def create_or_update_student_kp(data: StudentKPCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    existing = db.query(StudentKnowledgePoint).filter(
        StudentKnowledgePoint.student_id == data.student_id,
        StudentKnowledgePoint.knowledge_point_id == data.knowledge_point_id
    ).first()
    if existing:
        if data.mastery_level:
            existing.mastery_level = data.mastery_level
        if data.difficulty_level:
            existing.difficulty_level = data.difficulty_level
        if data.note:
            existing.note = data.note
        existing.study_count += 1
        existing.last_study_date = datetime.now()
        db.commit()
        db.refresh(existing)
        return existing
    record = StudentKnowledgePoint(
        student_id=data.student_id,
        knowledge_point_id=data.knowledge_point_id,
        mastery_level=data.mastery_level or "not_started",
        difficulty_level=data.difficulty_level or 3,
        note=data.note,
        study_count=1,
        last_study_date=datetime.now()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/student-kps/{kp_id}/")
def update_student_kp(kp_id: int, data: StudentKPUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    record = db.query(StudentKnowledgePoint).filter(StudentKnowledgePoint.id == kp_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.post("/student-kps/{kp_id}/tags/")
def add_kp_tags(kp_id: int, data: KPTagRelationCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    record = db.query(StudentKnowledgePoint).filter(StudentKnowledgePoint.id == kp_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    existing = db.query(KnowledgePointTagRelation).filter(
        KnowledgePointTagRelation.student_kp_id == kp_id,
        KnowledgePointTagRelation.tag_id == data.tag_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="标签已关联")
    rel = KnowledgePointTagRelation(student_kp_id=kp_id, tag_id=data.tag_id)
    db.add(rel)
    db.commit()
    return {"success": True, "message": "标签已添加"}


@router.delete("/student-kps/{kp_id}/tags/{tag_id}/")
def remove_kp_tag(kp_id: int, tag_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    rel = db.query(KnowledgePointTagRelation).filter(
        KnowledgePointTagRelation.student_kp_id == kp_id,
        KnowledgePointTagRelation.tag_id == tag_id
    ).first()
    if not rel:
        raise HTTPException(status_code=404, detail="关联不存在")
    db.delete(rel)
    db.commit()
    return {"success": True, "message": "标签已移除"}


@router.get("/student-kps/statistics/")
def student_kp_statistics(
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    query = db.query(StudentKnowledgePoint)
    if student_id:
        query = query.filter(StudentKnowledgePoint.student_id == student_id)
    records = query.all()
    mastery_dist = {"not_started": 0, "learning": 0, "practicing": 0, "mastered": 0}
    for r in records:
        level = r.mastery_level or "not_started"
        if level in mastery_dist:
            mastery_dist[level] += 1
    total_kps = db.query(KnowledgePoint).count()
    mastered_count = mastery_dist.get("mastered", 0)
    return {
        "total_student_kps": len(records),
        "mastery_distribution": mastery_dist,
        "overall_progress": round((mastered_count / total_kps * 100) if total_kps > 0 else 0, 2),
        "total_knowledge_points": total_kps,
    }


# ==================== 课程内容管理 ====================

@router.get("/course-contents/")
def list_course_contents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    content_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    chapter_id: Optional[int] = Query(None),
    knowledge_point_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    query = db.query(CourseContent)
    if content_type:
        query = query.filter(CourseContent.content_type == content_type)
    if status:
        query = query.filter(CourseContent.status == status)
    if chapter_id:
        query = query.filter(CourseContent.chapter_id == chapter_id)
    if knowledge_point_id:
        query = query.filter(CourseContent.knowledge_point_id == knowledge_point_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(or_(
            CourseContent.title.ilike(search_pattern),
            CourseContent.content.ilike(search_pattern)
        ))
    total = query.count()
    items = query.order_by(CourseContent.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    chapter_ids = {c.chapter_id for c in items if c.chapter_id}
    kp_ids = {c.knowledge_point_id for c in items if c.knowledge_point_id}
    chapter_map = {cid: title for cid, title in db.query(Chapter.id, Chapter.title).filter(Chapter.id.in_(chapter_ids)).all()} if chapter_ids else {}
    kp_map = {kid: content for kid, content in db.query(KnowledgePoint.id, KnowledgePoint.content).filter(KnowledgePoint.id.in_(kp_ids)).all()} if kp_ids else {}
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": c.id,
            "content_type": c.content_type,
            "title": c.title,
            "content": c.content,
            "content_metadata": c.content_metadata,
            "status": c.status,
            "chapter_id": c.chapter_id,
            "chapter_title": chapter_map.get(c.chapter_id),
            "knowledge_point_id": c.knowledge_point_id,
            "knowledge_point_content": kp_map.get(c.knowledge_point_id),
            "created_by": c.created_by,
            "published_at": c.published_at.isoformat() if c.published_at else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        } for c in items]
    }


@router.post("/course-contents/")
def create_course_content(data: CourseContentCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    content = CourseContent(
        content_type=data.content_type,
        title=data.title,
        content=data.content,
        content_metadata=data.content_metadata,
        status=data.status or "draft",
        chapter_id=data.chapter_id,
        knowledge_point_id=data.knowledge_point_id,
        created_by=data.created_by
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


@router.get("/course-contents/{content_id}/")
def get_course_content(content_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    content = db.query(CourseContent).filter(CourseContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="课程内容不存在")
    versions = db.query(CourseContentVersion).filter(
        CourseContentVersion.content_id == content_id
    ).order_by(CourseContentVersion.version_number.desc()).all()
    result = {
        "id": content.id,
        "content_type": content.content_type,
        "title": content.title,
        "content": content.content,
        "content_metadata": content.content_metadata,
        "status": content.status,
        "chapter_id": content.chapter_id,
        "knowledge_point_id": content.knowledge_point_id,
        "created_by": content.created_by,
        "published_at": content.published_at.isoformat() if content.published_at else None,
        "created_at": content.created_at.isoformat() if content.created_at else None,
        "updated_at": content.updated_at.isoformat() if content.updated_at else None,
        "versions": [{
            "id": v.id,
            "version_number": v.version_number,
            "title": v.title,
            "content": v.content,
            "content_metadata": v.content_metadata,
            "change_summary": v.change_summary,
            "created_by": v.created_by,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        } for v in versions]
    }
    return result


@router.put("/course-contents/{content_id}/")
def update_course_content(content_id: int, data: CourseContentUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    content = db.query(CourseContent).filter(CourseContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="课程内容不存在")
    if content.status == "published":
        raise HTTPException(status_code=400, detail="已发布内容不可直接修改，请创建新版本")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(content, key, value)
    db.commit()
    db.refresh(content)
    return content


@router.delete("/course-contents/{content_id}/")
def delete_course_content(content_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    content = db.query(CourseContent).filter(CourseContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="课程内容不存在")
    if content.status == "published":
        raise HTTPException(status_code=400, detail="已发布内容不可删除，请归档处理")
    db.query(CourseContentVersion).filter(CourseContentVersion.content_id == content_id).delete()
    db.delete(content)
    db.commit()
    return {"success": True, "message": "课程内容已删除"}


@router.post("/course-contents/{content_id}/publish/")
def publish_course_content(content_id: int, data: ContentPublishRequest, db: Session = Depends(get_db), admin=Depends(require_admin)):
    content = db.query(CourseContent).filter(CourseContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="课程内容不存在")
    if data.status not in ("published", "archived"):
        raise HTTPException(status_code=400, detail="发布状态只能是 published 或 archived")
    max_version = db.query(func.max(CourseContentVersion.version_number)).filter(
        CourseContentVersion.content_id == content_id
    ).scalar()
    new_version = (max_version or 0) + 1
    version = CourseContentVersion(
        content_id=content_id,
        version_number=new_version,
        title=content.title,
        content=content.content,
        content_metadata=content.content_metadata,
        change_summary=data.change_summary or f"发布版本 v{new_version}",
        created_by=content.created_by
    )
    db.add(version)
    content.status = data.status
    content.published_at = datetime.now() if data.status == "published" else content.published_at
    db.commit()
    db.refresh(content)
    return {
        "success": True,
        "message": f"已发布版本 v{new_version}",
        "version_number": new_version,
        "status": content.status
    }


@router.post("/course-contents/{content_id}/archive/")
def archive_course_content(content_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    content = db.query(CourseContent).filter(CourseContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="课程内容不存在")
    content.status = "archived"
    db.commit()
    return {"success": True, "message": "课程内容已归档"}


@router.get("/course-contents/{content_id}/versions/")
def list_content_versions(content_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    content = db.query(CourseContent).filter(CourseContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="课程内容不存在")
    versions = db.query(CourseContentVersion).filter(
        CourseContentVersion.content_id == content_id
    ).order_by(CourseContentVersion.version_number.desc()).all()
    return [{
        "id": v.id,
        "version_number": v.version_number,
        "title": v.title,
        "content": v.content,
        "content_metadata": v.content_metadata,
        "change_summary": v.change_summary,
        "created_by": v.created_by,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    } for v in versions]


@router.post("/course-contents/{content_id}/versions/")
def create_content_version(content_id: int, data: ContentPublishRequest, db: Session = Depends(get_db), admin=Depends(require_admin)):
    content = db.query(CourseContent).filter(CourseContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="课程内容不存在")
    max_version = db.query(func.max(CourseContentVersion.version_number)).filter(
        CourseContentVersion.content_id == content_id
    ).scalar()
    new_version = (max_version or 0) + 1
    version = CourseContentVersion(
        content_id=content_id,
        version_number=new_version,
        title=content.title,
        content=content.content,
        content_metadata=content.content_metadata,
        change_summary=data.change_summary or f"手动创建版本 v{new_version}",
        created_by=content.created_by
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return {
        "id": version.id,
        "version_number": version.version_number,
        "message": f"版本 v{new_version} 已创建"
    }


@router.post("/course-contents/{content_id}/versions/{version_id}/restore/")
def restore_content_version(content_id: int, version_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    content = db.query(CourseContent).filter(CourseContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="课程内容不存在")
    version = db.query(CourseContentVersion).filter(
        CourseContentVersion.id == version_id,
        CourseContentVersion.content_id == content_id
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")
    max_version = db.query(func.max(CourseContentVersion.version_number)).filter(
        CourseContentVersion.content_id == content_id
    ).scalar()
    new_version = (max_version or 0) + 1
    snapshot = CourseContentVersion(
        content_id=content_id,
        version_number=new_version,
        title=content.title,
        content=content.content,
        content_metadata=content.content_metadata,
        change_summary=f"恢复前快照（版本 v{version.version_number}）",
        created_by=content.created_by
    )
    db.add(snapshot)
    content.title = version.title
    content.content = version.content
    content.content_metadata = version.content_metadata
    db.commit()
    db.refresh(content)
    return {"success": True, "message": f"已恢复至版本 v{version.version_number}，当前内容已保存为 v{new_version}"}


# ==================== 题库管理 ====================

@router.get("/questions/")
def list_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    knowledge_point_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    query = db.query(Question)
    if knowledge_point_id:
        query = query.filter(Question.knowledge_point_id == knowledge_point_id)
    if type:
        query = query.filter(Question.type == type)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(or_(
            Question.stem.ilike(search_pattern),
            Question.answer.ilike(search_pattern)
        ))
    total = query.count()
    items = query.order_by(Question.order_index.asc(), Question.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
    kp_ids = list(set(q.knowledge_point_id for q in items))
    kp_map = {}
    if kp_ids:
        kps = db.query(KnowledgePoint).filter(KnowledgePoint.id.in_(kp_ids)).all()
        kp_map = {kp.id: kp for kp in kps}
    usage_map = {}
    if items:
        q_ids = [q.id for q in items]
        usages = db.query(QuestionUsage).filter(QuestionUsage.question_id.in_(q_ids)).all()
        for u in usages:
            usage_map[u.question_id] = u
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": q.id,
            "knowledge_point_id": q.knowledge_point_id,
            "kp_content": kp_map[q.knowledge_point_id].content if q.knowledge_point_id in kp_map else None,
            "type": q.type,
            "difficulty": q.difficulty,
            "stem": q.stem,
            "options": q.options,
            "answer": q.answer,
            "analysis": q.analysis,
            "image_resource": q.image_resource,
            "order_index": q.order_index,
            "usage_count": usage_map[q.id].usage_count if q.id in usage_map else 0,
            "created_at": q.created_at.isoformat() if q.created_at else None,
        } for q in items]
    }


@router.post("/questions/")
def create_question(data: QuestionCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == data.knowledge_point_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    question = Question(
        knowledge_point_id=data.knowledge_point_id,
        type=data.type,
        difficulty=data.difficulty or "medium",
        stem=data.stem,
        options=data.options,
        answer=data.answer,
        analysis=data.analysis,
        image_resource=data.image_resource,
        order_index=data.order_index or 0
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.get("/questions/{question_id}/")
def get_question(question_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    usage = db.query(QuestionUsage).filter(QuestionUsage.question_id == question_id).first()
    result = {
        "id": question.id,
        "knowledge_point_id": question.knowledge_point_id,
        "type": question.type,
        "difficulty": question.difficulty,
        "stem": question.stem,
        "options": question.options,
        "answer": question.answer,
        "analysis": question.analysis,
        "image_resource": question.image_resource,
        "order_index": question.order_index,
        "created_at": question.created_at.isoformat() if question.created_at else None,
        "usage": {
            "usage_count": usage.usage_count,
            "correct_count": usage.correct_count,
            "average_time_seconds": usage.average_time_seconds,
            "difficulty_rating": usage.difficulty_rating,
            "last_used_at": usage.last_used_at.isoformat() if usage.last_used_at else None,
        } if usage else None
    }
    return result


@router.put("/questions/{question_id}/")
def update_question(question_id: int, data: QuestionUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)
    db.commit()
    db.refresh(question)
    return question


@router.delete("/questions/{question_id}/")
def delete_question(question_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    db.query(QuestionUsage).filter(QuestionUsage.question_id == question_id).delete()
    db.delete(question)
    db.commit()
    return {"success": True, "message": "题目已删除"}


@router.post("/questions/batch-import/")
def batch_import_questions(data: QuestionBatchImport, db: Session = Depends(get_db), admin=Depends(require_admin)):
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == data.knowledge_point_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    created = 0
    skipped = 0
    errors = []
    for i, q_data in enumerate(data.questions):
        try:
            question = Question(
                knowledge_point_id=data.knowledge_point_id,
                type=q_data.get("type", "single_choice"),
                difficulty=q_data.get("difficulty", "medium"),
                stem=q_data["stem"],
                options=q_data.get("options"),
                answer=q_data["answer"],
                analysis=q_data.get("analysis"),
                image_resource=q_data.get("image_resource"),
                order_index=q_data.get("order_index", 0)
            )
            db.add(question)
            created += 1
        except Exception as e:
            skipped += 1
            errors.append({"index": i, "error": str(e)})
            if not data.skip_on_error:
                raise HTTPException(status_code=400, detail=f"第 {i + 1} 题导入失败: {str(e)}")
    db.commit()
    return {"created": created, "skipped": skipped, "errors": errors}


@router.post("/questions/export/")
def export_questions(data: QuestionExportRequest, db: Session = Depends(get_db), admin=Depends(require_admin)):
    query = db.query(Question)
    if data.knowledge_point_ids:
        query = query.filter(Question.knowledge_point_id.in_(data.knowledge_point_ids))
    if data.difficulty:
        query = query.filter(Question.difficulty == data.difficulty)
    if data.question_types:
        query = query.filter(Question.type.in_(data.question_types))
    questions = query.order_by(Question.knowledge_point_id, Question.order_index).all()
    kp_ids = list(set(q.knowledge_point_id for q in questions))
    kp_map = {}
    if kp_ids:
        kps = db.query(KnowledgePoint).filter(KnowledgePoint.id.in_(kp_ids)).all()
        kp_map = {kp.id: kp for kp in kps}
    rows = []
    for q in questions:
        row = {
            "id": q.id,
            "knowledge_point_id": q.knowledge_point_id,
            "kp_content": kp_map[q.knowledge_point_id].content if q.knowledge_point_id in kp_map else "",
            "type": q.type,
            "difficulty": q.difficulty,
            "stem": q.stem,
            "options": q.options,
            "answer": q.answer,
            "analysis": q.analysis if data.include_analysis else None,
            "order_index": q.order_index,
        }
        rows.append(row)
    return {
        "exported_at": datetime.now().isoformat(),
        "total": len(questions),
        "format": data.format,
        "headers": ["ID", "知识点ID", "知识点内容", "题型", "难度", "题干", "选项", "答案"] + (["解析"] if data.include_analysis else []),
        "rows": rows
    }


@router.get("/question-usage-stats/")
def questions_usage_stats(
    knowledge_point_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    query = db.query(Question)
    if knowledge_point_id:
        query = query.filter(Question.knowledge_point_id == knowledge_point_id)
    questions = query.all()
    if not questions:
        return {"total_questions": 0, "stats": [], "summary": {}}
    q_ids = [q.id for q in questions]
    usages = db.query(QuestionUsage).filter(QuestionUsage.question_id.in_(q_ids)).all()
    usage_map = {u.question_id: u for u in usages}
    stats = []
    for q in questions:
        u = usage_map.get(q.id)
        stats.append({
            "question_id": q.id,
            "knowledge_point_id": q.knowledge_point_id,
            "stem_preview": q.stem[:80] + "..." if len(q.stem) > 80 else q.stem,
            "type": q.type,
            "difficulty": q.difficulty,
            "usage_count": u.usage_count if u else 0,
            "correct_count": u.correct_count if u else 0,
            "accuracy_rate": round(u.correct_count / u.usage_count * 100, 2) if u and u.usage_count > 0 else None,
            "average_time_seconds": u.average_time_seconds if u else None,
            "difficulty_rating": u.difficulty_rating if u else None,
            "last_used_at": u.last_used_at.isoformat() if u and u.last_used_at else None,
        })
    total_usage = sum(s["usage_count"] for s in stats)
    total_correct = sum(s["correct_count"] for s in stats)
    answered = [s for s in stats if s["usage_count"] > 0]
    unanswered = [s for s in stats if s["usage_count"] == 0]
    return {
        "total_questions": len(questions),
        "total_usage": total_usage,
        "total_correct": total_correct,
        "overall_accuracy": round(total_correct / total_usage * 100, 2) if total_usage > 0 else None,
        "answered_count": len(answered),
        "unanswered_count": len(unanswered),
        "stats": sorted(stats, key=lambda x: x["usage_count"], reverse=True)
    }


# ==================== 可视化模板管理 ====================

@router.get("/viz-templates/")
def list_viz_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    chart_type: Optional[str] = Query(None),
    knowledge_point_id: Optional[int] = Query(None),
    is_public: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    query = db.query(VisualizationTemplate)
    if chart_type:
        query = query.filter(VisualizationTemplate.chart_type == chart_type)
    if knowledge_point_id:
        query = query.filter(VisualizationTemplate.knowledge_point_id == knowledge_point_id)
    if is_public is not None:
        query = query.filter(VisualizationTemplate.is_public == is_public)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(VisualizationTemplate.name.ilike(search_pattern))
    total = query.count()
    items = query.order_by(VisualizationTemplate.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    kp_ids = {t.knowledge_point_id for t in items if t.knowledge_point_id}
    kp_map = {kid: content for kid, content in db.query(KnowledgePoint.id, KnowledgePoint.content).filter(KnowledgePoint.id.in_(kp_ids)).all()} if kp_ids else {}
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": t.id,
            "name": t.name,
            "chart_type": t.chart_type,
            "config": t.config,
            "data_source": t.data_source,
            "is_public": t.is_public,
            "knowledge_point_id": t.knowledge_point_id,
            "knowledge_point_content": kp_map.get(t.knowledge_point_id),
            "created_by": t.created_by,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        } for t in items]
    }


@router.post("/viz-templates/")
def create_viz_template(data: VizTemplateCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    template = VisualizationTemplate(
        name=data.name,
        chart_type=data.chart_type,
        config=data.config,
        data_source=data.data_source,
        is_public=data.is_public,
        knowledge_point_id=data.knowledge_point_id,
        created_by=data.created_by
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/viz-templates/{template_id}/")
def get_viz_template(template_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    template = db.query(VisualizationTemplate).filter(VisualizationTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="可视化模板不存在")
    return template


@router.put("/viz-templates/{template_id}/")
def update_viz_template(template_id: int, data: VizTemplateUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    template = db.query(VisualizationTemplate).filter(VisualizationTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="可视化模板不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)
    db.commit()
    db.refresh(template)
    return template


@router.delete("/viz-templates/{template_id}/")
def delete_viz_template(template_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    template = db.query(VisualizationTemplate).filter(VisualizationTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="可视化模板不存在")
    db.delete(template)
    db.commit()
    return {"success": True, "message": "可视化模板已删除"}


@router.get("/viz-types/")
def list_viz_template_types(db: Session = Depends(get_db), admin=Depends(require_admin)):
    chart_types = {
        "line": "折线图",
        "bar": "柱状图",
        "pie": "饼图",
        "radar": "雷达图",
        "heatmap": "热力图",
        "scatter": "散点图",
        "gauge": "仪表盘",
        "funnel": "漏斗图"
    }
    type_counts = {}
    for ct in chart_types:
        count = db.query(VisualizationTemplate).filter(VisualizationTemplate.chart_type == ct).count()
        type_counts[ct] = count
    return {
        "chart_types": [{"key": k, "label": v} for k, v in chart_types.items()],
        "type_counts": type_counts,
        "total_templates": db.query(VisualizationTemplate).count()
    }
