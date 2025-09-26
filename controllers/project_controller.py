from sqlalchemy.orm import Session
from models.project import Project
from models.task import Task
from datetime import datetime

class ProjectController:
    def __init__(self, db: Session):
        self.db = db

    def get_projects_by_user(self, user_id: int):
        return self.db.query(Project).filter(Project.owner_id == user_id).all()

    def create_project(self, title: str, description: str, owner_id: int):
        project = Project(title=title, description=description, owner_id=owner_id)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update_project(self, project_id: int, new_title: str, new_description: str):
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.title = new_title
            project.description = new_description
            self.db.commit()
            self.db.refresh(project)
        return project

    def delete_project(self, project_id: int):
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if project:
            self.db.delete(project)
            self.db.commit()
            return True
        return False