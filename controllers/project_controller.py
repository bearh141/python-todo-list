from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db
from models.user import User
from models.project import Project
from models.task import Task
from sqlalchemy.orm import joinedload
from datetime import datetime

project_bp = Blueprint("project", __name__, url_prefix="/project")

@project_bp.route("/")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to view your dashboard.", "info")
        return redirect(url_for("auth.login"))

    db = next(get_db())
    user_id = session["user_id"]
    
    projects = db.query(Project).filter_by(owner_id=user_id).all()

    for p in projects:
        total_tasks = len(p.tasks)
        if total_tasks > 0:
            completed_tasks = sum(1 for task in p.tasks if task.completed)
            p.progress = int((completed_tasks / total_tasks) * 100)
        else:
            p.progress = 0

    return render_template("project/dashboard.html", projects=projects)

@project_bp.route("/create", methods=["GET", "POST"])
def create_project():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        
        if not title:
            flash("Project title is required.", "error")
            return redirect(url_for("project.create_project"))

        db = next(get_db())
        new_project = Project(
            title=title,
            description=description,
            owner_id=session["user_id"]
        )
        db.add(new_project)
        db.commit()
        flash(f"Project '{title}' created successfully!", "success")
        return redirect(url_for("project.dashboard"))

    return render_template("project/create_project.html")

@project_bp.route("/<int:project_id>")
def view_project(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    project = db.query(Project).options(joinedload(Project.tasks)).filter_by(id=project_id, owner_id=session["user_id"]).first()

    if not project:
        flash("Project not found or you don't have access.", "error")
        return redirect(url_for("project.dashboard"))
    tasks = sorted(project.tasks, key=lambda t: t.parent_id or -1)
    tasks_tree = {t.id: t for t in tasks}
    nested_tasks = []
    for t in tasks:
        if t.parent_id:
            parent = tasks_tree.get(t.parent_id)
            if parent:
                if not hasattr(parent, 'subtasks_list'):
                    parent.subtasks_list = []
                parent.subtasks_list.append(t)
        else:
            nested_tasks.append(t)
            
    return render_template("project/project_detail.html", project=project, tasks=nested_tasks)


# Xóa project
@project_bp.route("/delete/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    project = db.query(Project).filter_by(id=project_id, owner_id=session["user_id"]).first()

    if project:
        db.delete(project)
        db.commit()
        flash(f"Project '{project.title}' has been deleted.", "success")
    else:
        flash("Project not found or you don't have permission.", "error")
        
    return redirect(url_for("project.dashboard"))