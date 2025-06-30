from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class TaskLog(Base):
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(String, nullable=True)  # ✅ New column for traceability
    task_description = Column(String, nullable=False)
    task_type = Column(String)
    scheduled_duration = Column(Integer)
    actual_duration = Column(Integer, nullable=True)
    action = Column(String, nullable=False)  # 'c', 's', 'd', 'e'
    timestamp = Column(DateTime, default=datetime.utcnow)
