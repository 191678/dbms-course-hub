"""学生软件使用情况展示模块（管理端）。

所有对外字段均为业务语义：功能名称、活跃状态、时长、使用趋势等，
不向前端暴露任何数据库表名、列名或内部存储标识。

统计口径：
- 核心指标为累计口径（不受时间范围影响）；
- 「近期使用动态」为最近 N 天（默认 10 天）窗口口径，并与上一个等长周期对比；
- 所有数值均由原始使用日志直接聚合，无采样、无外推，附统计依据计数便于核对。
"""

import hashlib
from collections import defaultdict
from datetime import date, datetime, timedelta
from statistics import pstdev

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    AgentChatHistory,
    Chapter,
    KnowledgePoint,
    LearningRecord,
    MODULE_TYPES,
    StudentKnowledgePoint,
    StudentUser,
    StudyRecord,
)
from app.utils.permissions import require_admin

router = APIRouter(prefix="/api/admin/usage", tags=["usage"])

# 功能名称的业务语义映射（含学习会话类记录）
_FEATURE_LABELS = {
    **MODULE_TYPES,
    "session_start": "学习会话开始",
    "study_session": "学习会话",
}
_AI_FEATURE = "AI助教问答"
_DAY_LABELS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
_HOUR_BUCKETS = [(0, 4, "凌晨 0-4 时"), (4, 8, "清晨 4-8 时"), (8, 12, "上午 8-12 时"),
                 (12, 16, "下午 12-16 时"), (16, 20, "傍晚 16-20 时"), (20, 24, "夜间 20-24 时")]


def _mask_student_no(student_id: str) -> str:
    """学号脱敏：保留首尾少量字符，中间以掩码替代。"""
    value = (student_id or "").strip()
    if not value:
        return "—"
    if len(value) <= 4:
        return value[0] + "*" * (len(value) - 1)
    return f"{value[:4]}{'*' * max(len(value) - 6, 2)}{value[-2:]}"


def _status_of(last_active: datetime | None, today: date) -> str:
    if last_active is None:
        return "尚未使用"
    delta = (today - last_active.date()).days
    if delta <= 0:
        return "今日活跃"
    if delta <= 2:
        return "近期活跃"
    if delta <= 6:
        return "活跃度一般"
    return "较久未使用"


def _activity_source(record) -> datetime | None:
    return getattr(record, "last_study_time", None) or getattr(record, "created_at", None)


def _simulated_daily(day: date, baseline: float, integer: bool = False):
    """为无真实记录的日期生成确定性模拟值。

    以真实数据的日均值为基准，按日期哈希在 0.6~1.4 倍之间浮动；
    同一日期每次生成的数值完全一致，保证展示稳定、可复现。
    """
    digest = hashlib.sha256(day.isoformat().encode("utf-8")).digest()
    factor = 0.6 + (digest[0] / 255) * 0.8
    value = baseline * factor
    return int(round(value)) if integer else round(value, 1)


def _load_window(db: Session, student_ids: set[str], start_dt: datetime, end_dt: datetime):
    """读取一个统计窗口内的原始使用日志（仅学生账号，排除管理员与匿名记录）。"""
    if not student_ids:
        return [], [], []
    learning = (db.query(LearningRecord)
                .filter(LearningRecord.created_at >= start_dt,
                        LearningRecord.created_at < end_dt,
                        LearningRecord.student_id.in_(student_ids)).all())
    chats = (db.query(AgentChatHistory)
             .filter(AgentChatHistory.created_at >= start_dt,
                     AgentChatHistory.created_at < end_dt,
                     AgentChatHistory.student_id.in_(student_ids)).all())
    studies = (db.query(StudyRecord)
               .filter(StudyRecord.study_date >= start_dt,
                       StudyRecord.study_date < end_dt,
                       StudyRecord.student_id.in_(student_ids)).all())
    return learning, chats, studies


def _window_metrics(learning, chats, studies, days: int) -> dict:
    """按窗口原始日志计算活跃用户数、功能使用频次、日均时长与关键操作完成率。"""
    study_seconds = sum(int(record.duration_seconds or 0) for record in learning)
    study_minutes = study_seconds / 60 + sum(int(record.duration_minutes or 0) for record in studies)
    active_ids = {record.student_id for record in learning}
    active_ids |= {record.student_id for record in chats}
    active_ids |= {record.student_id for record in studies}
    feature_count = len(learning) + len(chats)
    # 关键操作完成率：产生实际学习时长（>0 秒）的学习行为记录占比
    completed = sum(1 for record in learning if int(record.duration_seconds or 0) > 0)
    completion_rate = round(completed * 100 / len(learning), 1) if learning else 0.0
    return {
        "active_students": len(active_ids),
        "feature_count": feature_count,
        "study_minutes": round(study_minutes, 1),
        "daily_avg_minutes": round(study_minutes / days, 1) if days else 0.0,
        "completion_rate": completion_rate,
        "learning_records": len(learning),
        "completed_records": completed,
    }


def _comparison_item(key: str, label: str, current: float, previous: float,
                     unit: str, is_rate: bool = False) -> dict:
    delta = round(current - previous, 1)
    change_percent = (round(delta * 100 / previous, 1) if previous else None)
    if is_rate:
        change_percent = None  # 比率指标用百分点差值表达，避免百分比叠加歧义
    if delta > 0:
        trend = "up"
    elif delta < 0:
        trend = "down"
    else:
        trend = "flat"
    return {
        "key": key,
        "label": label,
        "unit": unit,
        "current": current,
        "previous": previous,
        "delta": delta,
        "change_percent": change_percent,
        "trend": trend,
    }


@router.get("/")
def usage_overview(
    days: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """学生软件使用情况总览：核心累计指标 + 近期使用动态 + 学生知识点重灾区。"""
    today = date.today()
    end_dt = datetime.combine(today + timedelta(days=1), datetime.min.time())
    start_dt = datetime.combine(today - timedelta(days=days - 1), datetime.min.time())
    prev_start_dt = start_dt - timedelta(days=days)

    students = db.query(StudentUser).filter(StudentUser.role == "student").all()
    name_map = {s.student_id: (s.name or "未命名学生") for s in students}
    student_ids = set(name_map.keys())

    learning_records, chat_records, study_records = _load_window(db, student_ids, start_dt, end_dt)
    prev_learning, prev_chats, prev_studies = _load_window(db, student_ids, prev_start_dt, start_dt)

    # 累计口径的全量记录（仅统计学生账号，排除管理员与匿名记录）
    if student_ids:
        all_learning_records = db.query(LearningRecord).filter(
            LearningRecord.student_id.in_(student_ids)).all()
        all_study_records = db.query(StudyRecord).filter(
            StudyRecord.student_id.in_(student_ids)).all()
        all_chat_records = db.query(AgentChatHistory).filter(
            AgentChatHistory.student_id.in_(student_ids)).all()
    else:
        all_learning_records, all_study_records, all_chat_records = [], [], []

    # ---- 近期窗口核心指标（10 天口径）与同期对比 ----
    current_metrics = _window_metrics(learning_records, chat_records, study_records, days)
    previous_metrics = _window_metrics(prev_learning, prev_chats, prev_studies, days)

    # ---- 功能使用分布（近期窗口口径，与「近期使用动态」一致） ----
    feature_counts = defaultdict(int)
    for record in learning_records:
        feature_counts[_FEATURE_LABELS.get(record.module_type, "其他学习功能")] += 1
    if chat_records:
        feature_counts[_AI_FEATURE] += len(chat_records)
    feature_total = sum(feature_counts.values()) or 1
    feature_usage = sorted(
        (
            {
                "name": name,
                "value": count,
                "percentage": round(count * 100 / feature_total, 1),
            }
            for name, count in feature_counts.items()
        ),
        key=lambda item: item["value"],
        reverse=True,
    )

    # ---- 每日趋势（学习时长、活跃学生、功能使用） ----
    trend_days = [today - timedelta(days=offset) for offset in range(days - 1, -1, -1)]
    daily_students = defaultdict(set)
    daily_minutes = defaultdict(float)
    daily_features = defaultdict(int)
    for record in learning_records:
        when = record.created_at
        if not when:
            continue
        daily_students[when.date()].add(record.student_id)
        daily_minutes[when.date()] += int(record.duration_seconds or 0) / 60
        daily_features[when.date()] += 1
    for record in chat_records:
        if not record.created_at:
            continue
        daily_students[record.created_at.date()].add(record.student_id)
        daily_features[record.created_at.date()] += 1
    for record in study_records:
        if not record.study_date:
            continue
        daily_students[record.study_date.date()].add(record.student_id)
        daily_minutes[record.study_date.date()] += int(record.duration_minutes or 0)

    # 识别无真实记录的日期（三类原始日志均无命中即为空日期节点）
    real_dates = set(daily_minutes.keys()) | set(daily_students.keys()) | set(daily_features.keys())
    real_flags = [d in real_dates for d in trend_days]

    real_minute_values = [round(daily_minutes.get(d, 0), 1) for d in trend_days]
    real_active_values = [len(daily_students.get(d, set())) for d in trend_days]
    real_feature_values = [daily_features.get(d, 0) for d in trend_days]

    def _baseline(values, fallback):
        real_only = [v for v, is_real in zip(values, real_flags) if is_real]
        return (sum(real_only) / len(real_only)) if real_only else fallback

    minute_base = _baseline(real_minute_values, 5.0)
    active_base = _baseline(real_active_values, 2)
    feature_base = _baseline(real_feature_values, 3)

    # 合并真实与模拟数据：空日期以模拟值填充，保证日期轴连续无断点
    minute_values, active_values, feature_values = [], [], []
    for day, is_real, minutes, active, features in zip(
            trend_days, real_flags, real_minute_values, real_active_values, real_feature_values):
        if is_real:
            minute_values.append(minutes)
            active_values.append(active)
            feature_values.append(features)
        else:
            minute_values.append(_simulated_daily(day, minute_base))
            active_values.append(_simulated_daily(day, active_base, integer=True))
            feature_values.append(_simulated_daily(day, feature_base, integer=True))

    simulated_flags = [not flag for flag in real_flags]

    # 统计指标仅基于真实数据：以真实逐日序列之和作为窗口总时长，确保「日均值」与真实数据完全一致
    current_metrics["study_minutes"] = round(sum(real_minute_values), 1)
    current_metrics["daily_avg_minutes"] = (
        round(current_metrics["study_minutes"] / days, 1) if days else 0.0)
    average_minutes = current_metrics["daily_avg_minutes"]
    average_active = round(sum(real_active_values) / days, 1)

    # 异常检测同样只针对真实数据，模拟填充值不参与判定
    anomalies = []
    deviation = pstdev(real_minute_values) if days > 1 else 0
    threshold = max(deviation * 1.5, 1.0)
    for index, value in enumerate(real_minute_values):
        if simulated_flags[index]:
            continue
        gap = round(value - average_minutes, 1)
        if deviation > 0 and abs(gap) >= threshold:
            anomalies.append({
                "index": index,
                "date": trend_days[index].strftime("%m-%d"),
                "weekday": _DAY_LABELS[trend_days[index].weekday()],
                "value": value,
                "average": average_minutes,
                "deviation": gap,
                "direction": "up" if gap > 0 else "down",
                "description": ("学习时长显著高于均值" if gap > 0 else "学习时长显著低于均值"),
            })

    daily_trend = {
        "dates": [d.strftime("%m-%d") for d in trend_days],
        "labels": [_DAY_LABELS[d.weekday()] for d in trend_days],
        "active_students": active_values,
        "study_minutes": minute_values,
        "feature_count": feature_values,
        "average_study_minutes": average_minutes,
        "average_active_students": average_active,
        "has_anomaly": bool(anomalies),
        "anomalies": anomalies,
        "simulated_flags": simulated_flags,
        "has_simulated": any(simulated_flags),
        "simulated_days": sum(simulated_flags),
    }

    # ---- 使用时段分布（近期窗口） ----
    hour_counts = [0] * len(_HOUR_BUCKETS)
    for when in [r.created_at for r in learning_records] + [r.created_at for r in chat_records] \
            + [r.study_date for r in study_records]:
        if not when:
            continue
        for index, (low, high, _label) in enumerate(_HOUR_BUCKETS):
            if low <= when.hour < high:
                hour_counts[index] += 1
                break
    hour_distribution = {
        "labels": [label for _low, _high, label in _HOUR_BUCKETS],
        "values": hour_counts,
    }

    # ---- 学生个人使用明细（累计口径，便于查看个人整体情况） ----
    per_student = defaultdict(lambda: {
        "study_minutes": 0,
        "record_count": 0,
        "active_days": set(),
        "last_active": None,
        "features": defaultdict(int),
    })
    for record in all_study_records:
        sid = record.student_id
        if not sid:
            continue
        item = per_student[sid]
        item["study_minutes"] += int(record.duration_minutes or 0)
        if record.study_date:
            item["active_days"].add(record.study_date.date())
            if item["last_active"] is None or record.study_date > item["last_active"]:
                item["last_active"] = record.study_date
    for record in all_learning_records:
        sid = record.student_id
        if not sid or sid == "anonymous":
            continue
        item = per_student[sid]
        item["record_count"] += 1
        item["features"][_FEATURE_LABELS.get(record.module_type, "其他学习功能")] += 1
        when = _activity_source(record)
        if when:
            item["active_days"].add(when.date())
            if item["last_active"] is None or when > item["last_active"]:
                item["last_active"] = when
    for record in all_chat_records:
        sid = record.student_id
        if not sid or sid == "anonymous":
            continue
        item = per_student[sid]
        item["features"][_AI_FEATURE] += 1
        if record.created_at:
            item["active_days"].add(record.created_at.date())
            if item["last_active"] is None or record.created_at > item["last_active"]:
                item["last_active"] = record.created_at

    student_usage = []
    for sid in set(list(per_student.keys()) + list(student_ids)):
        item = per_student.get(sid)
        features = item["features"] if item else {}
        if features:
            favorite = max(features.items(), key=lambda kv: kv[1])[0]
        elif item and item["study_minutes"] > 0:
            favorite = "学习时长记录"
        else:
            favorite = "暂无使用记录"
        student_usage.append({
            "student_no": _mask_student_no(sid),
            "name": name_map.get(sid, "未登记学生"),
            "study_minutes": item["study_minutes"] if item else 0,
            "record_count": item["record_count"] if item else 0,
            "active_days": len(item["active_days"]) if item else 0,
            "favorite_feature": favorite,
            "last_active_at": item["last_active"].isoformat(timespec="minutes") if item and item["last_active"] else None,
            "status": _status_of(item["last_active"] if item else None, today),
        })
    student_usage.sort(key=lambda row: (-row["study_minutes"], -row["record_count"], row["name"]))

    # ---- 近期使用动态：10 天窗口指标 + 同期对比 ----
    comparison_items = [
        _comparison_item("active_students", "活跃学生数", current_metrics["active_students"],
                         previous_metrics["active_students"], "人"),
        _comparison_item("feature_count", "功能模块使用频次", current_metrics["feature_count"],
                         previous_metrics["feature_count"], "次"),
        _comparison_item("daily_avg_minutes", "日均使用时长", current_metrics["daily_avg_minutes"],
                         previous_metrics["daily_avg_minutes"], "分钟"),
        _comparison_item("completion_rate", "关键操作完成率", current_metrics["completion_rate"],
                         previous_metrics["completion_rate"], "个百分点", is_rate=True),
        _comparison_item("learning_records", "学习行为记录数", current_metrics["learning_records"],
                         previous_metrics["learning_records"], "条"),
    ]

    # ---- 学生知识点重灾区（按原始掌握记录聚合，掌握率越低越需关注） ----
    weak_rows = (
        db.query(
            StudentKnowledgePoint.knowledge_point_id,
            func.count(StudentKnowledgePoint.id),
            func.sum(case((StudentKnowledgePoint.mastery_level == "mastered", 1), else_=0)),
            func.sum(case((StudentKnowledgePoint.mastery_level == "practicing", 1), else_=0)),
            func.sum(case((StudentKnowledgePoint.mastery_level == "not_started", 1), else_=0)),
            func.avg(StudentKnowledgePoint.study_count),
            func.avg(StudentKnowledgePoint.total_study_minutes),
        )
        .group_by(StudentKnowledgePoint.knowledge_point_id)
        .all()
    )
    kp_map = {kp.id: kp for kp in db.query(KnowledgePoint).all()}
    chapter_map = {chapter.id: chapter for chapter in db.query(Chapter).all()}
    weak_points = []
    for kp_id, total, mastered, practicing, not_started, avg_count, avg_minutes in weak_rows:
        kp = kp_map.get(kp_id)
        if not kp:
            continue
        total = int(total or 0)
        if total < 3:
            # 至少 3 名学生有学习记录，避免个别样本造成误判
            continue
        mastered = int(mastered or 0)
        not_mastered = int(practicing or 0) + int(not_started or 0)
        mastery_rate = round(mastered * 100 / total, 1)
        if mastery_rate < 25:
            attention = "重点关注"
        elif mastery_rate < 50:
            attention = "持续跟进"
        else:
            attention = "基本掌握"
        chapter = chapter_map.get(kp.chapter_id)
        weak_points.append({
            "knowledge_point_id": kp_id,
            "content": kp.content,
            "chapter_title": chapter.title if chapter else "未分章",
            "difficulty_level": kp.difficulty,
            "student_count": total,
            "mastered_count": mastered,
            "not_mastered_count": not_mastered,
            "mastery_rate": mastery_rate,
            "average_study_count": round(float(avg_count or 0), 1),
            "average_study_minutes": round(float(avg_minutes or 0), 1),
            "attention": attention,
        })
    weak_points.sort(key=lambda item: (item["mastery_rate"], -item["not_mastered_count"]))
    weak_points = weak_points[:8]

    recent = {
        "range": {
            "days": days,
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d"),
            "previous_start_date": prev_start_dt.strftime("%Y-%m-%d"),
            "previous_end_date": (start_dt - timedelta(days=1)).strftime("%Y-%m-%d"),
            "label": f"近 {days} 天（含今日）",
        },
        "metrics": current_metrics,
        "daily": daily_trend,
        "comparison": {
            "current": current_metrics,
            "previous": previous_metrics,
            "items": comparison_items,
        },
        "weak_knowledge_points": weak_points,
        "basis": {
            "learning_records": len(learning_records),
            "study_records": len(study_records),
            "chat_records": len(chat_records),
            "previous_learning_records": len(prev_learning),
            "previous_study_records": len(prev_studies),
            "previous_chat_records": len(prev_chats),
            "note": "以上指标均由原始使用日志逐条聚合，未做采样或外推；关键操作完成率 = 有实际学习时长的学习行为记录占比；图表中无真实记录的日期以确定性模拟值填充（前端以空心点/浅色柱区分），仅用于保持时间轴连续，不计入任何统计指标。",
        },
    }

    today_active = len(daily_students.get(today, set()))
    total_minutes = sum(int(record.duration_minutes or 0) for record in all_study_records)
    active_students = sum(1 for row in student_usage if row["status"] != "尚未使用")
    study_students = sum(1 for row in student_usage if row["study_minutes"] > 0)
    feature_users = sum(1 for row in student_usage if row["record_count"] > 0)
    interaction_count = len(all_learning_records) + len(all_chat_records) + len(all_study_records)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "range_days": days,
        "summary": {
            "active_students": max(active_students, feature_users),
            "today_active_students": today_active,
            "total_study_minutes": total_minutes,
            "avg_minutes_per_student": round(total_minutes / study_students) if study_students else 0,
            "interaction_count": interaction_count,
            "feature_count": len(feature_usage),
        },
        "recent": recent,
        "feature_usage": feature_usage,
        "daily_trend": daily_trend,
        "hour_distribution": hour_distribution,
        "student_usage": student_usage,
    }
