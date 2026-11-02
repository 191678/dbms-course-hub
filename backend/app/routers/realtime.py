"""实时数据同步服务。

通过给数据库内容计算一个“数据版本指纹”，只要任一业务数据表发生新增、
修改或删除，指纹就会变化。前端可订阅 SSE 推送，也可轮询轻量版本接口，
两者都能在 1 秒内感知变更并刷新展示内容。
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy import text

from app.database import SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/realtime", tags=["realtime"])

# 参与变更检测的业务表及其时间字段（无 updated_at 的表使用 created_at）
_MONITORED_TABLES = [
    ("chapters", "updated_at"),
    ("knowledge_points", "updated_at"),
    ("questions", "updated_at"),
    ("student_users", "updated_at"),
    ("learning_records", "updated_at"),
    ("study_records", "updated_at"),
    ("study_statistics", "updated_at"),
    ("student_knowledge_points", "updated_at"),
    ("knowledge_point_tags", "created_at"),
    ("knowledge_point_tag_relations", "created_at"),
    ("course_contents", "updated_at"),
    ("course_content_versions", "created_at"),
    ("question_usages", "updated_at"),
    ("visualization_templates", "updated_at"),
    ("agent_chat_history", "created_at"),
    ("roles", "created_at"),
    ("permissions", "created_at"),
    ("role_permissions", "created_at"),
    ("user_roles", "created_at"),
]

_FINGERPRINT_SQL = text(" UNION ALL ".join(
    f"SELECT '{table}' AS t, COUNT(*) AS c, COALESCE(CAST(MAX({column}) AS CHAR), '') AS m FROM {table}"
    for table, column in _MONITORED_TABLES
))

# 轮询间隔（秒）：保证服务端在 1 秒内发现数据变化
_POLL_INTERVAL = 0.5
# 心跳间隔（秒）：避免代理长时间无数据断开连接
_HEARTBEAT_INTERVAL = 15.0


def compute_data_version() -> str:
    """计算当前数据的版本指纹；数据库不可用时返回空字符串。"""
    db = SessionLocal()
    try:
        rows = db.execute(_FINGERPRINT_SQL).fetchall()
        raw = "|".join(f"{row[0]}:{row[1]}:{row[2]}" for row in rows)
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]
    except Exception as exc:  # 数据库短暂不可用不应中断推送
        logger.warning("计算数据版本失败: %s", exc)
        return ""
    finally:
        db.close()


@router.get("/version/")
def get_data_version():
    """返回当前数据版本，供前端轮询做兜底同步。"""
    return {
        "version": compute_data_version(),
        "server_time": datetime.now().isoformat(timespec="seconds"),
    }


async def _event_stream(request: Request):
    last_version = await asyncio.to_thread(compute_data_version)
    payload = {
        "version": last_version,
        "server_time": datetime.now().isoformat(timespec="seconds"),
    }
    yield f"event: ready\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

    loop = asyncio.get_event_loop()
    last_beat = loop.time()
    while True:
        if await request.is_disconnected():
            break
        await asyncio.sleep(_POLL_INTERVAL)
        current = await asyncio.to_thread(compute_data_version)
        now = loop.time()
        if current and current != last_version:
            last_version = current
            payload = {
                "version": current,
                "server_time": datetime.now().isoformat(timespec="seconds"),
            }
            yield f"event: data-change\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
            last_beat = now
        elif now - last_beat >= _HEARTBEAT_INTERVAL:
            last_beat = now
            yield ": keep-alive\n\n"


@router.websocket("/ws/")
async def data_ws(websocket: WebSocket):
    """WebSocket 长连接推送通道（前端优先使用）。

    服务端每 0.5 秒计算一次数据版本指纹，发现变化立即推送；
    客户端心跳消息同时用于连接活性检测，断开时自动结束循环。
    """
    await websocket.accept()
    last_version = await asyncio.to_thread(compute_data_version)
    await websocket.send_json({
        "type": "ready",
        "version": last_version,
        "server_time": datetime.now().isoformat(timespec="seconds"),
    })
    try:
        while True:
            try:
                # 接收客户端心跳（内容不重要），超时则进入版本检查
                await asyncio.wait_for(websocket.receive_text(), timeout=_POLL_INTERVAL)
            except asyncio.TimeoutError:
                pass
            current = await asyncio.to_thread(compute_data_version)
            if current and current != last_version:
                last_version = current
                await websocket.send_json({
                    "type": "data-change",
                    "version": current,
                    "server_time": datetime.now().isoformat(timespec="seconds"),
                })
    except WebSocketDisconnect:
        pass
    except Exception as exc:  # 网络中断等异常仅结束当前连接
        logger.debug("WebSocket 连接结束: %s", exc)


@router.get("/stream/")
async def data_stream(request: Request):
    """SSE 推送接口：数据发生变化时立即通知前端刷新。"""
    return StreamingResponse(
        _event_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
