from pydantic import BaseModel, field_validator
from typing import Optional, List
import re
from datetime import datetime


class ChapterBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int = 0


class ChapterCreate(ChapterBase):
    pass


class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None


class ChapterResponse(ChapterBase):
    id: int
    knowledge_points: List['KnowledgePointResponse'] = []

    model_config = {"from_attributes": True}


class KnowledgePointBase(BaseModel):
    content: str
    summary: Optional[str] = None
    difficulty: str = "medium"
    category: Optional[str] = None
    detail_content: Optional[str] = None
    key_points: Optional[List[str]] = None
    image_prompt: Optional[str] = None
    video_script: Optional[str] = None
    learning_steps: Optional[List[str]] = None
    tips: Optional[List[str]] = None
    faq: Optional[List[dict]] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None
    order_index: int = 0


class KnowledgePointCreate(KnowledgePointBase):
    chapter_id: int


class KnowledgePointUpdate(BaseModel):
    content: Optional[str] = None
    summary: Optional[str] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    detail_content: Optional[str] = None
    key_points: Optional[List[str]] = None
    image_prompt: Optional[str] = None
    video_script: Optional[str] = None
    learning_steps: Optional[List[str]] = None
    tips: Optional[List[str]] = None
    faq: Optional[List[dict]] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None
    order_index: Optional[int] = None


class KnowledgePointResponse(KnowledgePointBase):
    id: int
    chapter_id: int
    children: List['KnowledgePointResponse'] = []
    questions: List['QuestionResponse'] = []

    model_config = {"from_attributes": True}


class QuestionBase(BaseModel):
    type: str
    difficulty: str = "medium"
    stem: str
    options: Optional[List[str]] = None
    answer: str
    analysis: Optional[str] = None
    image_resource: Optional[str] = None
    order_index: int = 0


class QuestionCreate(QuestionBase):
    knowledge_point_id: int


class QuestionUpdate(BaseModel):
    type: Optional[str] = None
    difficulty: Optional[str] = None
    stem: Optional[str] = None
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    analysis: Optional[str] = None
    image_resource: Optional[str] = None
    order_index: Optional[int] = None


class QuestionResponse(QuestionBase):
    id: int
    knowledge_point_id: int

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    student_question: str
    context: Optional[dict] = None
    student_id: Optional[str] = None


class MediaData(BaseModel):
    media_type: str
    format: str
    content: Optional[str] = None
    title: Optional[str] = None
    steps: Optional[List[dict]] = None
    slides: Optional[List[dict]] = None
    full_speech: Optional[str] = None
    duration: Optional[str] = None
    duration_seconds: Optional[int] = None
    slides_count: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    tool_used: Optional[str] = None
    context: Optional[dict] = None
    media_data: Optional[MediaData] = None
    questions: Optional[List[dict]] = None


class AgentHistoryItem(BaseModel):
    id: int
    question: str
    created_at: Optional[str] = None


class AgentHistoryResponse(BaseModel):
    student_id: str
    questions: List[AgentHistoryItem] = []


class GeneratedQuestion(BaseModel):
    id: int
    type: str
    stem: str
    options: Optional[List[str]] = None
    answer: str
    analysis: str


class VisualizeRequest(BaseModel):
    topic: str


class VisualizationDiagram(BaseModel):
    media_type: str
    format: str
    content: str
    title: str


class VisualizationResponse(BaseModel):
    success: bool
    knowledge_point: Optional[str] = None
    chapter: Optional[str] = None
    category: Optional[str] = None
    definition: Optional[str] = None
    key_points: Optional[List[str]] = None
    theory_content: Optional[str] = None
    diagram: Optional[VisualizationDiagram] = None
    relationship_explanation: Optional[str] = None


class SlideItem(BaseModel):
    slide_number: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    speech: Optional[str] = None
    duration: Optional[int] = None


class SlidesAudioRequest(BaseModel):
    slides: List[SlideItem]


class SlidesAudioResponse(BaseModel):
    success: bool
    audio_urls: List[str] = []
    total: int = 0
    failed_indexes: List[int] = []
    error: Optional[str] = None


# ==================== 认证相关 Schema ====================

STUDENT_ID_PATTERN = re.compile(r'^\d{6,20}$')


class StudentRegisterRequest(BaseModel):
    student_id: str
    username: str
    password: str
    name: str = ""

    @field_validator('student_id')
    @classmethod
    def validate_student_id(cls, v):
        if not STUDENT_ID_PATTERN.match(v):
            raise ValueError('学号格式错误，应为6-20位数字')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度不能少于6位')
        if len(v) > 100:
            raise ValueError('密码长度不能超过100位')
        return v

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 2:
            raise ValueError('用户名长度不能少于2位')
        if len(v) > 50:
            raise ValueError('用户名长度不能超过50位')
        return v


class StudentLoginRequest(BaseModel):
    account: str
    password: str

    @field_validator('account')
    @classmethod
    def validate_account(cls, v):
        if not v or len(v) < 2:
            raise ValueError('账号不能为空')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v:
            raise ValueError('密码不能为空')
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class StudentUserResponse(BaseModel):
    id: int
    student_id: str
    username: str
    name: str
    role: str
    is_active: bool
    last_login_at: Optional[str] = None
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('新密码长度不能少于6位')
        return v


# ==================== 学习进度相关 Schema ====================

class LearningRecordBase(BaseModel):
    session_id: str
    student_id: str = "anonymous"
    module_type: str
    module_id: Optional[str] = None
    module_name: Optional[str] = None
    knowledge_point_id: Optional[int] = None
    knowledge_point_content: Optional[str] = None
    duration_seconds: int = 0
    study_duration_minutes: int = 0
    status: str = "viewing"
    completion_percentage: float = 0.0
    interaction_count: int = 0
    last_study_time: Optional[str] = None
    mastered_count: int = 0
    not_mastered_count: int = 0
    extra_data: Optional[dict] = None

    @field_validator('completion_percentage')
    @classmethod
    def validate_completion_percentage(cls, v):
        if v < 0 or v > 100:
            raise ValueError('完成百分比必须在0-100之间')
        return v

    @field_validator('mastered_count', 'not_mastered_count')
    @classmethod
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError('数量不能为负数')
        return v


class LearningRecordCreate(LearningRecordBase):
    pass


class LearningRecordUpdate(BaseModel):
    module_name: Optional[str] = None
    duration_seconds: Optional[int] = None
    study_duration_minutes: Optional[int] = None
    status: Optional[str] = None
    completion_percentage: Optional[float] = None
    interaction_count: Optional[int] = None
    last_study_time: Optional[str] = None
    mastered_count: Optional[int] = None
    not_mastered_count: Optional[int] = None
    extra_data: Optional[dict] = None


class LearningRecordResponse(LearningRecordBase):
    id: int
    record_uuid: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class LearningRecordBatchCreate(BaseModel):
    records: List[LearningRecordCreate]


class LearningProgressSummary(BaseModel):
    total_duration_seconds: int = 0
    total_study_minutes: int = 0
    total_records: int = 0
    modules_visited: List[str] = []
    knowledge_points_learned: List[dict] = []
    module_statistics: dict = {}
    overall_completion_percentage: float = 0.0


class LearningRecordQuery(BaseModel):
    student_id: Optional[str] = None
    module_type: Optional[str] = None
    knowledge_point_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ModuleProgressDetail(BaseModel):
    module_uuid: str
    module_name: str
    completion_percentage: float
    last_study_time: Optional[str] = None
    study_duration_minutes: int
    mastered_count: int
    not_mastered_count: int


class StudentProgressOverview(BaseModel):
    student_id: str
    total_study_minutes: int
    total_modules_accessed: int
    overall_completion_percentage: float
    module_progress_list: List[ModuleProgressDetail] = []
    last_learning_time: Optional[str] = None


ChapterResponse.update_forward_refs()
KnowledgePointResponse.update_forward_refs()
