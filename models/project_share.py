from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base

class ProjectShare(Base):
    __tablename__ = "project_shares"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum('viewer', 'editor', name='role_enum'), default='viewer')

    project = relationship("Project", back_populates="shares")
    user = relationship("User")