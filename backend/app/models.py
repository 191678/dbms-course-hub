from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    knowledge_points = relationship("KnowledgePoint", back_populates="chapter", cascade="all, delete-orphan")


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    difficulty = Column(String(20), nullable=False, default="medium", index=True)
    category = Column(String(50), nullable=True, index=True)
    detail_content = Column(Text, nullable=True)
    key_points = Column(JSON, nullable=True)
    image_prompt = Column(Text, nullable=True)
    video_script = Column(Text, nullable=True)
    learning_steps = Column(JSON, nullable=True)
    tips = Column(JSON, nullable=True)
    faq = Column(JSON, nullable=True)
    image_url = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    chapter = relationship("Chapter", back_populates="knowledge_points")
    parent = relationship("KnowledgePoint", remote_side=[id], back_populates="children")
    children = relationship("KnowledgePoint", back_populates="parent", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="knowledge_point", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False, index=True)
    type = Column(String(20), nullable=False, index=True)
    difficulty = Column(String(20), nullable=False, default="medium", index=True)
    stem = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)
    answer = Column(Text, nullable=False)
    analysis = Column(Text, nullable=True)
    image_resource = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    knowledge_point = relationship("KnowledgePoint", back_populates="questions")


class StudentUser(Base):
    __tablename__ = "student_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(50), nullable=False, default="")
    role = Column(String(20), nullable=False, default="student", index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    learning_records = relationship("LearningRecord", back_populates="student_user", cascade="all, delete-orphan")


class LearningRecord(Base):
    __tablename__ = "learning_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_uuid = Column(String(36), unique=True, nullable=False, default=generate_uuid, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    student_id = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("student_users.id"), nullable=True, index=True)
    module_type = Column(String(50), nullable=False, index=True)
    module_id = Column(String(36), nullable=True, index=True)
    module_name = Column(String(200), nullable=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True, index=True)
    knowledge_point_content = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=False, default=0)
    study_duration_minutes = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="viewing", index=True)
    completion_percentage = Column(Float, nullable=False, default=0.0)
    interaction_count = Column(Integer, nullable=False, default=0)
    last_recorded_duration = Column(Integer, nullable=False, default=0)
    last_study_time = Column(DateTime, nullable=True)
    mastered_count = Column(Integer, nullable=False, default=0)
    not_mastered_count = Column(Integer, nullable=False, default=0)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    knowledge_point = relationship("KnowledgePoint")
    student_user = relationship("StudentUser", back_populates="learning_records")


# ==================== RBAC 权限模型 ====================

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)
    is_system = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())

    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    codename = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)
    module = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("student_users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("StudentUser")
    role = relationship("Role", back_populates="user_roles")


# ==================== 学习时间管理模型 ====================

class StudyRecord(Base):
    __tablename__ = "study_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), nullable=False, index=True)
    course_name = Column(String(200), nullable=True)
    chapter_name = Column(String(200), nullable=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True, index=True)
    knowledge_point_content = Column(String(500), nullable=True)
    study_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False, default=0)
    study_type = Column(String(30), nullable=False, default="self", index=True)
    is_abnormal = Column(Boolean, nullable=False, default=False, index=True)
    abnormal_reason = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    source = Column(String(20), nullable=False, default="auto")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    knowledge_point = relationship("KnowledgePoint")


class StudyStatistics(Base):
    __tablename__ = "study_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), nullable=False, index=True)
    stat_type = Column(String(20), nullable=False, index=True)
    stat_period = Column(String(20), nullable=False, index=True)
    stat_date = Column(DateTime, nullable=False, index=True)
    total_minutes = Column(Integer, nullable=False, default=0)
    session_count = Column(Integer, nullable=False, default=0)
    abnormal_count = Column(Integer, nullable=False, default=0)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ==================== 疑难知识点管理模型 ====================

class KnowledgePointTag(Base):
    __tablename__ = "knowledge_point_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False, default="custom", index=True)
    parent_id = Column(Integer, ForeignKey("knowledge_point_tags.id"), nullable=True, index=True)
    color = Column(String(20), nullable=True)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    parent = relationship("KnowledgePointTag", remote_side=[id])


class StudentKnowledgePoint(Base):
    __tablename__ = "student_knowledge_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), nullable=False, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False, index=True)
    mastery_level = Column(String(20), nullable=False, default="not_started", index=True)
    difficulty_level = Column(Integer, nullable=False, default=3)
    last_study_date = Column(DateTime, nullable=True)
    study_count = Column(Integer, nullable=False, default=0)
    total_study_minutes = Column(Integer, nullable=False, default=0)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    knowledge_point = relationship("KnowledgePoint")


class KnowledgePointTagRelation(Base):
    __tablename__ = "knowledge_point_tag_relations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_kp_id = Column(Integer, ForeignKey("student_knowledge_points.id"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("knowledge_point_tags.id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())


# ==================== 课程内容管理模型 ====================

class CourseContent(Base):
    __tablename__ = "course_contents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_type = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    content_metadata = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="draft", index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("student_users.id"), nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    chapter = relationship("Chapter")
    knowledge_point = relationship("KnowledgePoint")


class CourseContentVersion(Base):
    __tablename__ = "course_content_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Integer, ForeignKey("course_contents.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    content_metadata = Column(JSON, nullable=True)
    change_summary = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey("student_users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class QuestionUsage(Base):
    __tablename__ = "question_usages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    usage_count = Column(Integer, nullable=False, default=0)
    correct_count = Column(Integer, nullable=False, default=0)
    average_time_seconds = Column(Integer, nullable=True)
    difficulty_rating = Column(Float, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    question = relationship("Question")


class VisualizationTemplate(Base):
    __tablename__ = "visualization_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    chart_type = Column(String(50), nullable=False, index=True)
    config = Column(JSON, nullable=False)
    data_source = Column(String(200), nullable=True)
    is_public = Column(Boolean, nullable=False, default=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("student_users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AgentChatHistory(Base):
    __tablename__ = "agent_chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), nullable=False, index=True)
    question = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)


MODULE_TYPES = {
    "knowledge_visualization": "知识可视化",
    "knowledge_graph": "知识关联图谱",
    "theory_content": "理论内容",
    "key_points": "关键要点",
    "diagram": "图表展示",
    "agent_interaction": "AI助教交互",
    "search": "知识搜索",
    "node_click": "节点点击"
}
