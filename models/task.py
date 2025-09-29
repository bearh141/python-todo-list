from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

task_tags = Table('task_tags', Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(Enum('low', 'medium', 'high', name='priority_enum'), default='medium')
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reminder_sent = Column(Boolean, default=False)

    # Quan hệ
    project = relationship("Project", back_populates="tasks")
    user = relationship("User", back_populates="tasks")
    parent = relationship("Task", remote_side=[id], back_populates="subtasks")
    subtasks = relationship("Task", back_populates="parent", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="task_tags", back_populates="tasks")