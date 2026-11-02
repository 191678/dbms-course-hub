from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import StudentUser, Role, Permission, UserRole, RolePermission
from app.utils.auth import decode_access_token, get_current_user_role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def require_admin(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token无效或已过期")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token数据异常")

    user = db.query(StudentUser).filter(StudentUser.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已被禁用")

    if user.role not in ("admin", "teacher"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足，需要管理员权限")

    return user


def get_current_admin_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return require_admin(token, db)


def check_permission(user_id: int, permission_codename: str, db: Session) -> bool:
    user = db.query(StudentUser).filter(StudentUser.id == user_id).first()
    if not user:
        return False

    if user.role in ("admin", "teacher"):
        return True

    user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    role_ids = [ur.role_id for ur in user_roles]

    if not role_ids:
        return False

    permissions = (
        db.query(Permission)
        .join(RolePermission, Permission.id == RolePermission.permission_id)
        .filter(RolePermission.role_id.in_(role_ids))
        .filter(Permission.codename == permission_codename)
        .first()
    )

    return permissions is not None


def require_permission(permission_codename: str):
    def dependency(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        user = require_admin(token, db)

        if user.role in ("admin", "teacher"):
            return user

        if not check_permission(user.id, permission_codename, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {permission_codename}",
            )
        return user

    return dependency


def init_rbac_data(db: Session):
    default_permissions = [
        {"name": "查看学生", "codename": "student.view", "module": "student", "description": "查看学生列表和详情"},
        {"name": "管理学生", "codename": "student.manage", "module": "student", "description": "添加、编辑、删除学生"},
        {"name": "查看学习时间", "codename": "study_time.view", "module": "study_time", "description": "查看学生学习时间"},
        {"name": "管理学习时间", "codename": "study_time.manage", "module": "study_time", "description": "手动录入、编辑学习时间"},
        {"name": "导入导出学习时间", "codename": "study_time.import_export", "module": "study_time", "description": "批量导入导出学习时间数据"},
        {"name": "查看知识点", "codename": "knowledge_point.view", "module": "knowledge_point", "description": "查看知识点列表"},
        {"name": "管理知识点", "codename": "knowledge_point.manage", "module": "knowledge_point", "description": "添加、编辑、删除知识点"},
        {"name": "查看课程内容", "codename": "course_content.view", "module": "course_content", "description": "查看课程首页内容"},
        {"name": "管理课程内容", "codename": "course_content.manage", "module": "course_content", "description": "编辑、发布课程内容"},
        {"name": "管理题库", "codename": "question.manage", "module": "question", "description": "题目增删改查和导入导出"},
        {"name": "查看题库统计", "codename": "question.stats", "module": "question", "description": "查看题目使用统计"},
        {"name": "管理可视化模板", "codename": "visualization.manage", "module": "visualization", "description": "创建和管理可视化模板"},
    ]

    for perm_data in default_permissions:
        existing = db.query(Permission).filter(Permission.codename == perm_data["codename"]).first()
        if not existing:
            perm = Permission(**perm_data)
            db.add(perm)

    db.flush()

    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="系统管理员", is_system=True)
        db.add(admin_role)
        db.flush()

    teacher_role = db.query(Role).filter(Role.name == "teacher").first()
    if not teacher_role:
        teacher_role = Role(name="teacher", description="教师", is_system=True)
        db.add(teacher_role)
        db.flush()

    student_role = db.query(Role).filter(Role.name == "student").first()
    if not student_role:
        student_role = Role(name="student", description="学生", is_system=True)
        db.add(student_role)
        db.flush()

    all_permissions = db.query(Permission).all()
    for perm in all_permissions:
        existing_rp = db.query(RolePermission).filter(
            RolePermission.role_id == admin_role.id,
            RolePermission.permission_id == perm.id
        ).first()
        if not existing_rp:
            db.add(RolePermission(role_id=admin_role.id, permission_id=perm.id))

    teacher_perms = ["student.view", "study_time.view", "knowledge_point.view", "knowledge_point.manage",
                     "course_content.view", "course_content.manage", "question.manage", "question.stats",
                     "visualization.manage"]
    for codename in teacher_perms:
        perm = db.query(Permission).filter(Permission.codename == codename).first()
        if perm:
            existing_rp = db.query(RolePermission).filter(
                RolePermission.role_id == teacher_role.id,
                RolePermission.permission_id == perm.id
            ).first()
            if not existing_rp:
                db.add(RolePermission(role_id=teacher_role.id, permission_id=perm.id))

    admin_user = db.query(StudentUser).filter(StudentUser.username == "admin").first()
    if admin_user:
        existing_ur = db.query(UserRole).filter(
            UserRole.user_id == admin_user.id,
            UserRole.role_id == admin_role.id
        ).first()
        if not existing_ur:
            db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))

    db.commit()
