from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
from datetime import datetime, date
import re


# ==================== RBAC 权限管理 Schema ====================

PERMISSION_CODENAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]*:[a-z][a-z0-9_]*$')


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('角色名称不能为空')
        if len(v) > 50:
            raise ValueError('角色名称长度不能超过50个字符')
        return v


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('角色名称不能为空')
            if len(v) > 50:
                raise ValueError('角色名称长度不能超过50个字符')
        return v


class RoleResponse(RoleBase):
    id: int
    is_system: bool = False
    created_at: Optional[datetime] = None
    permissions: List['PermissionResponse'] = []
    user_count: int = 0

    model_config = {"from_attributes": True}


class PermissionBase(BaseModel):
    name: str
    codename: str
    description: Optional[str] = None
    module: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('权限名称不能为空')
        if len(v) > 100:
            raise ValueError('权限名称长度不能超过100个字符')
        return v

    @field_validator('codename')
    @classmethod
    def validate_codename(cls, v):
        if not v or not v.strip():
            raise ValueError('权限代码不能为空')
        if len(v) > 100:
            raise ValueError('权限代码长度不能超过100个字符')
        if not PERMISSION_CODENAME_PATTERN.match(v):
            raise ValueError('权限代码格式错误，应为"module:action"格式（如 chapter:create）')
        return v

    @field_validator('module')
    @classmethod
    def validate_module(cls, v):
        if not v or not v.strip():
            raise ValueError('所属模块不能为空')
        if len(v) > 50:
            raise ValueError('模块名称长度不能超过50个字符')
        return v


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserRoleCreate(BaseModel):
    user_id: int
    role_id: int

    @field_validator('user_id', 'role_id')
    @classmethod
    def validate_positive_id(cls, v):
        if v <= 0:
            raise ValueError('ID必须为正整数')
        return v


class UserRoleResponse(BaseModel):
    id: int
    user_id: int
    role_id: int
    created_at: Optional[datetime] = None
    user: Optional[dict] = None
    role: Optional[RoleResponse] = None

    model_config = {"from_attributes": True}


# ==================== 学习时间管理 Schema ====================

STUDY_TYPE_CHOICES = {"self", "class", "exam", "review", "other"}
SOURCE_CHOICES = {"auto", "manual", "import"}


class StudyRecordBase(BaseModel):
    student_id: str
    course_name: Optional[str] = None
    chapter_name: Optional[str] = None
    knowledge_point_id: Optional[int] = None
    knowledge_point_content: Optional[str] = None
    study_date: datetime
    duration_minutes: int = 0
    study_type: str = "self"
    is_abnormal: bool = False
    abnormal_reason: Optional[str] = None
    notes: Optional[str] = None
    source: str = "auto"

    @field_validator('student_id')
    @classmethod
    def validate_student_id(cls, v):
        if not v or not v.strip():
            raise ValueError('学生ID不能为空')
        if len(v) > 50:
            raise ValueError('学生ID长度不能超过50个字符')
        return v

    @field_validator('duration_minutes')
    @classmethod
    def validate_duration_minutes(cls, v):
        if v < 0:
            raise ValueError('学习时长不能为负数')
        if v > 1440:
            raise ValueError('学习时长不能超过1440分钟（24小时）')
        return v

    @field_validator('study_type')
    @classmethod
    def validate_study_type(cls, v):
        if v not in STUDY_TYPE_CHOICES:
            raise ValueError(f'学习类型无效，可选值：{", ".join(sorted(STUDY_TYPE_CHOICES))}')
        return v

    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        if v not in SOURCE_CHOICES:
            raise ValueError(f'数据来源无效，可选值：{", ".join(sorted(SOURCE_CHOICES))}')
        return v

    @field_validator('study_date')
    @classmethod
    def validate_study_date(cls, v):
        if v > datetime.now():
            raise ValueError('学习日期不能是未来时间')
        return v

    @field_validator('is_abnormal')
    @classmethod
    def validate_abnormal_reason(cls, v, info):
        if v and not info.data.get('abnormal_reason'):
            raise ValueError('异常记录必须填写异常原因')
        return v


class StudyRecordCreate(StudyRecordBase):
    pass


class StudyRecordUpdate(BaseModel):
    course_name: Optional[str] = None
    chapter_name: Optional[str] = None
    knowledge_point_id: Optional[int] = None
    knowledge_point_content: Optional[str] = None
    study_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    study_type: Optional[str] = None
    is_abnormal: Optional[bool] = None
    abnormal_reason: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('duration_minutes')
    @classmethod
    def validate_duration_minutes(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError('学习时长不能为负数')
            if v > 1440:
                raise ValueError('学习时长不能超过1440分钟（24小时）')
        return v

    @field_validator('study_type')
    @classmethod
    def validate_study_type(cls, v):
        if v is not None and v not in STUDY_TYPE_CHOICES:
            raise ValueError(f'学习类型无效，可选值：{", ".join(sorted(STUDY_TYPE_CHOICES))}')
        return v

    @field_validator('study_date')
    @classmethod
    def validate_study_date(cls, v):
        if v is not None and v > datetime.now():
            raise ValueError('学习日期不能是未来时间')
        return v


class StudyRecordResponse(StudyRecordBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StudyStatisticsResponse(BaseModel):
    id: int
    student_id: str
    stat_type: str
    stat_period: str
    stat_date: datetime
    total_minutes: int = 0
    session_count: int = 0
    abnormal_count: int = 0
    details: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BatchImportRequest(BaseModel):
    records: List[StudyRecordCreate]
    skip_on_error: bool = False

    @field_validator('records')
    @classmethod
    def validate_records(cls, v):
        if not v:
            raise ValueError('导入记录不能为空')
        if len(v) > 500:
            raise ValueError('单次导入记录数不能超过500条')
        return v


# ==================== 疑难知识点管理 Schema ====================

MASTERY_LEVEL_CHOICES = {"not_started", "learning", "practicing", "mastered"}
DIFFICULTY_LEVEL_MIN = 1
DIFFICULTY_LEVEL_MAX = 5
TAG_CATEGORY_CHOICES = {"custom", "difficulty", "importance", "error_prone", "exam_focus"}


class TagBase(BaseModel):
    name: str
    category: str = "custom"
    parent_id: Optional[int] = None
    color: Optional[str] = None
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('标签名称不能为空')
        if len(v) > 50:
            raise ValueError('标签名称长度不能超过50个字符')
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v not in TAG_CATEGORY_CHOICES:
            raise ValueError(f'标签分类无效，可选值：{", ".join(sorted(TAG_CATEGORY_CHOICES))}')
        return v

    @field_validator('parent_id')
    @classmethod
    def validate_parent_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError('父级标签ID必须为正整数')
        return v

    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        if v is not None and v:
            if not re.match(r'^#[0-9a-fA-F]{6}$', v):
                raise ValueError('颜色值必须为十六进制格式（如 #FF5733）')
        return v


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    parent_id: Optional[int] = None
    color: Optional[str] = None
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('标签名称不能为空')
            if len(v) > 50:
                raise ValueError('标签名称长度不能超过50个字符')
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v is not None and v not in TAG_CATEGORY_CHOICES:
            raise ValueError(f'标签分类无效，可选值：{", ".join(sorted(TAG_CATEGORY_CHOICES))}')
        return v

    @field_validator('parent_id')
    @classmethod
    def validate_parent_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError('父级标签ID必须为正整数')
        return v

    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        if v is not None and v:
            if not re.match(r'^#[0-9a-fA-F]{6}$', v):
                raise ValueError('颜色值必须为十六进制格式（如 #FF5733）')
        return v


class TagResponse(TagBase):
    id: int
    created_at: Optional[datetime] = None
    children: List['TagResponse'] = []

    model_config = {"from_attributes": True}


class StudentKPBase(BaseModel):
    student_id: str
    knowledge_point_id: int
    mastery_level: str = "not_started"
    difficulty_level: int = 3
    last_study_date: Optional[datetime] = None
    study_count: int = 0
    total_study_minutes: int = 0
    note: Optional[str] = None

    @field_validator('student_id')
    @classmethod
    def validate_student_id(cls, v):
        if not v or not v.strip():
            raise ValueError('学生ID不能为空')
        return v

    @field_validator('knowledge_point_id')
    @classmethod
    def validate_kp_id(cls, v):
        if v <= 0:
            raise ValueError('知识点ID必须为正整数')
        return v

    @field_validator('mastery_level')
    @classmethod
    def validate_mastery_level(cls, v):
        if v not in MASTERY_LEVEL_CHOICES:
            raise ValueError(f'掌握程度无效，可选值：{", ".join(sorted(MASTERY_LEVEL_CHOICES))}')
        return v

    @field_validator('difficulty_level')
    @classmethod
    def validate_difficulty_level(cls, v):
        if not DIFFICULTY_LEVEL_MIN <= v <= DIFFICULTY_LEVEL_MAX:
            raise ValueError(f'难度等级必须在{DIFFICULTY_LEVEL_MIN}-{DIFFICULTY_LEVEL_MAX}之间')
        return v

    @field_validator('study_count', 'total_study_minutes')
    @classmethod
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError('数值不能为负数')
        return v


class StudentKPCreate(StudentKPBase):
    pass


class StudentKPUpdate(BaseModel):
    mastery_level: Optional[str] = None
    difficulty_level: Optional[int] = None
    last_study_date: Optional[datetime] = None
    study_count: Optional[int] = None
    total_study_minutes: Optional[int] = None
    note: Optional[str] = None

    @field_validator('mastery_level')
    @classmethod
    def validate_mastery_level(cls, v):
        if v is not None and v not in MASTERY_LEVEL_CHOICES:
            raise ValueError(f'掌握程度无效，可选值：{", ".join(sorted(MASTERY_LEVEL_CHOICES))}')
        return v

    @field_validator('difficulty_level')
    @classmethod
    def validate_difficulty_level(cls, v):
        if v is not None:
            if not DIFFICULTY_LEVEL_MIN <= v <= DIFFICULTY_LEVEL_MAX:
                raise ValueError(f'难度等级必须在{DIFFICULTY_LEVEL_MIN}-{DIFFICULTY_LEVEL_MAX}之间')
        return v

    @field_validator('study_count', 'total_study_minutes')
    @classmethod
    def validate_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('数值不能为负数')
        return v


class StudentKPResponse(StudentKPBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List['TagResponse'] = []

    model_config = {"from_attributes": True}


class KPTagRelationCreate(BaseModel):
    student_kp_id: int
    tag_id: int

    @field_validator('student_kp_id', 'tag_id')
    @classmethod
    def validate_positive_id(cls, v):
        if v <= 0:
            raise ValueError('ID必须为正整数')
        return v


# ==================== 课程内容管理 Schema ====================

CONTENT_TYPE_CHOICES = {"text", "video", "audio", "pdf", "interactive", "quiz"}
CONTENT_STATUS_CHOICES = {"draft", "published", "archived", "review"}


class CourseContentBase(BaseModel):
    content_type: str
    title: str
    content: Optional[str] = None
    content_metadata: Optional[dict] = None
    status: str = "draft"
    chapter_id: Optional[int] = None
    knowledge_point_id: Optional[int] = None

    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v):
        if v not in CONTENT_TYPE_CHOICES:
            raise ValueError(f'内容类型无效，可选值：{", ".join(sorted(CONTENT_TYPE_CHOICES))}')
        return v

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('内容标题不能为空')
        if len(v) > 200:
            raise ValueError('标题长度不能超过200个字符')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in CONTENT_STATUS_CHOICES:
            raise ValueError(f'状态无效，可选值：{", ".join(sorted(CONTENT_STATUS_CHOICES))}')
        return v

    @field_validator('chapter_id', 'knowledge_point_id')
    @classmethod
    def validate_optional_positive_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError('ID必须为正整数')
        return v


class CourseContentCreate(CourseContentBase):
    created_by: Optional[int] = None


class CourseContentUpdate(BaseModel):
    content_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    content_metadata: Optional[dict] = None
    status: Optional[str] = None
    chapter_id: Optional[int] = None
    knowledge_point_id: Optional[int] = None

    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v):
        if v is not None and v not in CONTENT_TYPE_CHOICES:
            raise ValueError(f'内容类型无效，可选值：{", ".join(sorted(CONTENT_TYPE_CHOICES))}')
        return v

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('内容标题不能为空')
            if len(v) > 200:
                raise ValueError('标题长度不能超过200个字符')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in CONTENT_STATUS_CHOICES:
            raise ValueError(f'状态无效，可选值：{", ".join(sorted(CONTENT_STATUS_CHOICES))}')
        return v

    @field_validator('chapter_id', 'knowledge_point_id')
    @classmethod
    def validate_optional_positive_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError('ID必须为正整数')
        return v


class CourseContentResponse(CourseContentBase):
    id: int
    created_by: Optional[int] = None
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    versions: List['ContentVersionResponse'] = []

    model_config = {"from_attributes": True}


class ContentVersionResponse(BaseModel):
    id: int
    content_id: int
    version_number: int
    title: str
    content: Optional[str] = None
    content_metadata: Optional[dict] = None
    change_summary: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ContentPublishRequest(BaseModel):
    status: str = "published"
    change_summary: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in {"published", "archived"}:
            raise ValueError('发布状态只能是 published 或 archived')
        return v


# ==================== 题目管理 Schema ====================

QUESTION_TYPE_CHOICES = {"single_choice", "multiple_choice", "true_false", "fill_blank", "short_answer", "essay"}


class QuestionBatchImport(BaseModel):
    knowledge_point_id: int
    questions: List[dict]
    skip_on_error: bool = False

    @field_validator('knowledge_point_id')
    @classmethod
    def validate_kp_id(cls, v):
        if v <= 0:
            raise ValueError('知识点ID必须为正整数')
        return v

    @field_validator('questions')
    @classmethod
    def validate_questions(cls, v):
        if not v:
            raise ValueError('题目列表不能为空')
        if len(v) > 200:
            raise ValueError('单次导入题目数不能超过200条')
        for i, q in enumerate(v):
            if not q.get('stem'):
                raise ValueError(f'第 {i + 1} 道题缺少题干')
            if not q.get('answer'):
                raise ValueError(f'第 {i + 1} 道题缺少答案')
        return v


class QuestionExportRequest(BaseModel):
    knowledge_point_ids: Optional[List[int]] = None
    difficulty: Optional[str] = None
    question_types: Optional[List[str]] = None
    include_analysis: bool = True
    format: str = "json"

    @field_validator('knowledge_point_ids')
    @classmethod
    def validate_kp_ids(cls, v):
        if v is not None:
            for kp_id in v:
                if kp_id <= 0:
                    raise ValueError('知识点ID必须为正整数')
        return v

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v is not None and v not in {"easy", "medium", "hard"}:
            raise ValueError('难度等级无效，可选值：easy, medium, hard')
        return v

    @field_validator('question_types')
    @classmethod
    def validate_question_types(cls, v):
        if v is not None:
            for qt in v:
                if qt not in QUESTION_TYPE_CHOICES:
                    raise ValueError(f'题目类型无效：{qt}')
        return v

    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        if v not in {"json", "csv", "markdown", "docx"}:
            raise ValueError('导出格式无效，可选值：json, csv, markdown, docx')
        return v


class QuestionUsageResponse(BaseModel):
    id: int
    question_id: int
    usage_count: int = 0
    correct_count: int = 0
    average_time_seconds: Optional[int] = None
    difficulty_rating: Optional[float] = None
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    accuracy_rate: Optional[float] = None

    model_config = {"from_attributes": True}


class DifficultyLevelUpdate(BaseModel):
    question_ids: List[int]
    difficulty: str

    @field_validator('question_ids')
    @classmethod
    def validate_question_ids(cls, v):
        if not v:
            raise ValueError('题目ID列表不能为空')
        for qid in v:
            if qid <= 0:
                raise ValueError('题目ID必须为正整数')
        return v

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v not in {"easy", "medium", "hard"}:
            raise ValueError('难度等级无效，可选值：easy, medium, hard')
        return v


# ==================== 可视化模板管理 Schema ====================

CHART_TYPE_CHOICES = {"line", "bar", "pie", "radar", "heatmap", "scatter", "gauge", "funnel"}


class VizTemplateBase(BaseModel):
    name: str
    chart_type: str
    config: dict
    data_source: Optional[str] = None
    is_public: bool = True
    knowledge_point_id: Optional[int] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('模板名称不能为空')
        if len(v) > 100:
            raise ValueError('模板名称长度不能超过100个字符')
        return v

    @field_validator('chart_type')
    @classmethod
    def validate_chart_type(cls, v):
        if v not in CHART_TYPE_CHOICES:
            raise ValueError(f'图表类型无效，可选值：{", ".join(sorted(CHART_TYPE_CHOICES))}')
        return v

    @field_validator('config')
    @classmethod
    def validate_config(cls, v):
        if not v:
            raise ValueError('图表配置不能为空')
        if len(str(v)) > 50000:
            raise ValueError('配置内容过大')
        return v

    @field_validator('knowledge_point_id')
    @classmethod
    def validate_kp_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError('知识点ID必须为正整数')
        return v


class VizTemplateCreate(VizTemplateBase):
    created_by: Optional[int] = None


class VizTemplateUpdate(BaseModel):
    name: Optional[str] = None
    chart_type: Optional[str] = None
    config: Optional[dict] = None
    data_source: Optional[str] = None
    is_public: Optional[bool] = None
    knowledge_point_id: Optional[int] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('模板名称不能为空')
            if len(v) > 100:
                raise ValueError('模板名称长度不能超过100个字符')
        return v

    @field_validator('chart_type')
    @classmethod
    def validate_chart_type(cls, v):
        if v is not None and v not in CHART_TYPE_CHOICES:
            raise ValueError(f'图表类型无效，可选值：{", ".join(sorted(CHART_TYPE_CHOICES))}')
        return v

    @field_validator('config')
    @classmethod
    def validate_config(cls, v):
        if v is not None:
            if not v:
                raise ValueError('图表配置不能为空')
            if len(str(v)) > 50000:
                raise ValueError('配置内容过大')
        return v

    @field_validator('knowledge_point_id')
    @classmethod
    def validate_kp_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError('知识点ID必须为正整数')
        return v


class VizTemplateResponse(VizTemplateBase):
    id: int
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ==================== 前向引用更新 ====================

RoleResponse.model_rebuild(force=True)
PermissionResponse.model_rebuild(force=True)
TagResponse.model_rebuild(force=True)
StudentKPResponse.model_rebuild(force=True)
CourseContentResponse.model_rebuild(force=True)
ContentVersionResponse.model_rebuild(force=True)
VizTemplateResponse.model_rebuild(force=True)
UserRoleResponse.model_rebuild(force=True)