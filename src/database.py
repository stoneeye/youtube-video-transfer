from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import enum
import os

Base = declarative_base()

class Status(enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    FAILED = "failed"

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(Integer, primary_key=True)
    youtube_id = Column(String, unique=True, nullable=False)
    title = Column(String)
    url = Column(String)
    filepath = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=True)
    bilibili_bvid = Column(String, nullable=True)
    status = Column(Enum(Status), default=Status.PENDING)
    error_msg = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db(db_path: str = "data/history.db"):
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
