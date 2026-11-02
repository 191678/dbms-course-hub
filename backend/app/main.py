from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.routers import chapters, knowledge_points, questions, agent, knowledge_graph, learning_progress, auth, admin, usage, realtime
from app.database import engine, SessionLocal, Base
from app.models import StudentUser, Chapter, KnowledgePoint, MODULE_TYPES
from app.utils.auth import hash_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DBMS Course Hub API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(chapters.router, prefix="/api/chapters", tags=["chapters"])
app.include_router(knowledge_points.router, prefix="/api/knowledge_points", tags=["knowledge_points"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(knowledge_graph.router, prefix="/api/knowledge_graph", tags=["knowledge_graph"])
app.include_router(learning_progress.router, prefix="/api/learning-progress", tags=["learning_progress"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, tags=["admin"])
app.include_router(usage.router, tags=["usage"])
app.include_router(realtime.router, tags=["realtime"])


def init_database():
    logger.info("开始初始化数据库...")
    
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")
    
    from app.seed_data import seed_students, seed_chapters_and_knowledge_points, seed_questions
    from app.seed_data import seed_study_records, seed_student_kps, seed_course_content
    from app.seed_data import seed_viz_templates, seed_kp_tags, seed_rbac

    db = SessionLocal()
    try:
        logger.info("填充种子数据...")
        seed_students()
        kp_map = seed_chapters_and_knowledge_points()
        seed_questions(kp_map)
        seed_study_records()
        seed_student_kps()
        seed_course_content()
        seed_viz_templates()
        seed_kp_tags()
        seed_rbac()
        logger.info("种子数据填充完成")
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        db.rollback()
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    init_database()


frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

@app.options("/api/{full_path:path}")
async def api_options(full_path: str):
    return {"detail": "CORS preflight allowed"}

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_dist, "index.html"))

@app.get("/{full_path:path}")
async def catch_all_get(full_path: str):
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    return FileResponse(os.path.join(frontend_dist, "index.html"))
