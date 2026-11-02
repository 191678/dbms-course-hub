from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set")
    sys.exit(1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # 使用前检查连接健康，避免"MySQL server has gone away"
    pool_recycle=3600,        # 每3600秒回收连接，防止MySQL端已关闭的死连接
    pool_size=10,             # 连接池大小
    max_overflow=20,          # 允许的溢出连接数
    pool_timeout=30,          # 获取连接超时时间(秒)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
