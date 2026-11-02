from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models import StudentUser, LearningRecord
# 学习概况统计说明：会话类模块（study_session/session_start）不计入"访问模块"
from app.schemas import (
    StudentRegisterRequest,
    StudentLoginRequest,
    TokenResponse,
    StudentUserResponse,
    ChangePasswordRequest
)
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token数据异常",
        )
    
    user = db.query(StudentUser).filter(StudentUser.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )
    
    return user


@router.post("/register", response_model=StudentUserResponse)
def register_student(data: StudentRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(StudentUser).filter(
        (StudentUser.student_id == data.student_id) | 
        (StudentUser.username == data.username)
    ).first()
    
    if existing:
        if existing.student_id == data.student_id:
            raise HTTPException(status_code=400, detail="该学号已注册")
        raise HTTPException(status_code=400, detail="该用户名已被使用")
    
    user = StudentUser(
        student_id=data.student_id,
        username=data.username,
        password_hash=hash_password(data.password),
        name=data.name or data.username
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login_student(data: StudentLoginRequest, db: Session = Depends(get_db)):
    user = db.query(StudentUser).filter(
        (StudentUser.student_id == data.account) | 
        (StudentUser.username == data.account)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学号或密码错误"
        )
    
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学号或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "student_id": user.student_id,
            "username": user.username,
            "role": user.role
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "student_id": user.student_id,
            "username": user.username,
            "name": user.name,
            "role": user.role
        }
    )


@router.get("/profile", response_model=StudentUserResponse)
def get_profile(current_user: StudentUser = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "student_id": current_user.student_id,
        "username": current_user.username,
        "name": current_user.name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


@router.post("/logout")
def logout(current_user: StudentUser = Depends(get_current_user)):
    return {"success": True, "message": "已退出登录"}


@router.put("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: StudentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"success": True, "message": "密码修改成功"}


@router.get("/students/{student_id}/progress")
def get_student_progress(
    student_id: str,
    db: Session = Depends(get_db)
):
    try:
        return _get_student_progress_impl(student_id, db)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def _get_student_progress_impl(student_id: str, db: Session):
    records = db.query(LearningRecord).filter(
        LearningRecord.student_id == student_id
    ).all()
    
    if not records:
        return {
            "student_id": student_id,
            "total_study_minutes": 0,
            "total_modules_accessed": 0,
            "overall_completion_percentage": 0.0,
            "module_progress_list": [],
            "last_learning_time": None
        }
    
    module_stats = {}
    ignored_module_types = {'study_session', 'session_start'}
    for r in records:
        mt = r.module_type
        if mt in ignored_module_types:
            continue
        if mt not in module_stats:
            module_stats[mt] = {
                "module_uuid": r.record_uuid if r.record_uuid else mt,
                "module_name": r.module_name or mt,
                "completion_percentage": 0.0,
                "last_study_time": None,
                "last_study_time_dt": None,
                "study_duration_minutes": 0,
                "mastered_count": 0,
                "not_mastered_count": 0
            }
        module_stats[mt]["study_duration_minutes"] += r.study_duration_minutes or 0
        module_stats[mt]["mastered_count"] += r.mastered_count or 0
        module_stats[mt]["not_mastered_count"] += r.not_mastered_count or 0
        if r.completion_percentage > module_stats[mt]["completion_percentage"]:
            module_stats[mt]["completion_percentage"] = r.completion_percentage
        if r.last_study_time:
            if not module_stats[mt]["last_study_time_dt"] or r.last_study_time > module_stats[mt]["last_study_time_dt"]:
                module_stats[mt]["last_study_time_dt"] = r.last_study_time
                module_stats[mt]["last_study_time"] = r.last_study_time.isoformat()
        if r.updated_at:
            if not module_stats[mt]["last_study_time_dt"] or r.updated_at > module_stats[mt]["last_study_time_dt"]:
                module_stats[mt]["last_study_time_dt"] = r.updated_at
                module_stats[mt]["last_study_time"] = r.updated_at.isoformat()
    
    total_duration = sum(r.duration_seconds or 0 for r in records)
    total_minutes = sum(r.study_duration_minutes or 0 for r in records)
    module_list = list(module_stats.values())
    
    for m in module_list:
        m.pop("last_study_time_dt", None)
    
    overall_completion = 0.0
    if module_list:
        overall_completion = sum(m["completion_percentage"] for m in module_list) / len(module_list)
    
    last_time = None
    if records:
        latest = max(records, key=lambda r: r.updated_at or r.created_at)
        last_time = latest.updated_at.isoformat() if latest.updated_at else None
    
    return {
        "student_id": student_id,
        "total_study_minutes": max(total_minutes, total_duration // 60),
        "total_modules_accessed": len(module_list),
        "overall_completion_percentage": round(overall_completion, 2),
        "module_progress_list": module_list,
        "last_learning_time": last_time
    }
