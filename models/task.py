from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from datetime import datetime
from database import Base

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now())