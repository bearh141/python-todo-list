from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response
from database import get_db
from models.user import User
from models.project import Project
from models.task import Task
from models.project_share import ProjectShare
from sqlalchemy.orm import joinedload
from datetime import datetime
import csv
from io import StringIO

project_bp = Blueprint("project", __name__, url_prefix="/project")

@project_bp.route("/")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to view your dashboard.", "info")
        return redirect(url_for("auth.login"))

    db = next(get_db())
    user_id = session["user_id"]
    
    search_query = request.args.get("search", "")
    projects = db.query(Project).filter_by(owner_id=user_id)
    if search_query:
        projects = projects.filter(Project.title.like(f"%{search_query}%"))
    projects = projects.all()
    
    for p in projects:
        total_tasks = len(p.tasks)
        p.progress = int((sum(1 for task in p.tasks if task.completed) / total_tasks) * 100) if total_tasks > 0 else 0

    return render_template("project/dashboard.html", projects=projects, search_query=search_query)

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
        if db.query(Project).filter_by(title=title, owner_id=session["user_id"]).first():
            flash("Project title already exists.", "error")
            return redirect(url_for("project.create_project"))

        new_project = Project(title=title, description=description, owner_id=session["user_id"])
        db.add(new_project)
        db.commit()
        flash(f"Project '{title}' created successfully!", "success")
        return redirect(url_for("project.dashboard"))

    return render_template("project/create_project.html")

@project_bp.route("/edit/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    project = db.query(Project).filter_by(id=project_id, owner_id=session["user_id"]).first()
    if not project:
        flash("Project not found or you don't have access.", "error")
        return redirect(url_for("project.dashboard"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        if not title:
            flash("Project title is required.", "error")
            return render_template("project/edit_project.html", project=project)

        if db.query(Project).filter_by(title=title, owner_id=session["user_id"]).filter(Project.id != project_id).first():
            flash("Project title already exists.", "error")
            return render_template("project/edit_project.html", project=project)

        project.title = title
        project.description = description
        db.commit()
        flash("Project updated successfully!", "success")
        return redirect(url_for("project.dashboard"))

    return render_template("project/edit_project.html", project=project)

@project_bp.route("/<int:project_id>")
def view_project(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    project = db.query(Project).options(joinedload(Project.tasks)).filter_by(id=project_id).first()
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("project.dashboard"))

    # Kiểm tra quyền: owner hoặc shared user
    is_owner = project.owner_id == session["user_id"]
    share = db.query(ProjectShare).filter_by(project_id=project_id, user_id=session["user_id"]).first()
    if not (is_owner or share):
        flash("You don't have access to this project.", "error")
        return redirect(url_for("project.dashboard"))

    role = share.role if share else 'owner'

    search_query = request.args.get("search", "")
    completed_filter = request.args.get("completed", None)
    tasks = db.query(Task).filter_by(project_id=project_id)
    if search_query:
        tasks = tasks.filter(Task.title.like(f"%{search_query}%"))
    if completed_filter is not None:
        tasks = tasks.filter(Task.completed == (completed_filter == "true"))
    tasks = sorted(tasks.all(), key=lambda t: (t.parent_id or -1, {'high': 0, 'medium': 1, 'low': 2}.get(t.priority, 1)))

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

    return render_template("project/project_detail.html", project=project, tasks=nested_tasks, role=role, search_query=search_query, completed_filter=completed_filter)

@project_bp.route("/delete/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    project = db.query(Project).filter_by(id=project_id, owner_id=session["user_id"]).first()
    if not project:
        flash("Project not found or you don't have permission.", "error")
        return redirect(url_for("project.dashboard"))

    db.delete(project)
    db.commit()
    flash(f"Project '{project.title}' has been deleted.", "success")
    return redirect(url_for("project.dashboard"))

@project_bp.route("/invite/<int:project_id>", methods=["GET", "POST"])
def invite_user(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    project = db.query(Project).filter_by(id=project_id, owner_id=session["user_id"]).first()
    if not project:
        flash("Project not found or you don't have permission.", "error")
        return redirect(url_for("project.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        role = request.form.get("role")
        user = db.query(User).filter_by(email=email).first()
        if not user:
            flash("User not found.", "error")
            return render_template("project/invite_user.html", project=project)
        if user.id == session["user_id"]:
            flash("Cannot invite yourself.", "error")
            return render_template("project/invite_user.html", project=project)
        if db.query(ProjectShare).filter_by(project_id=project_id, user_id=user.id).first():
            flash("User already invited.", "error")
            return render_template("project/invite_user.html", project=project)

        share = ProjectShare(project_id=project_id, user_id=user.id, role=role)
        db.add(share)
        db.commit()
        flash(f"Invited {email} successfully!", "success")
        return redirect(url_for("project.view_project", project_id=project_id))

    return render_template("project/invite_user.html", project=project)

@project_bp.route("/export/<int:project_id>")
def export_project(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    project = db.query(Project).filter_by(id=project_id, owner_id=session["user_id"]).first()
    if not project:
        flash("Project not found or you don't have access.", "error")
        return redirect(url_for("project.dashboard"))

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Task ID", "Title", "Description", "Due Date", "Completed", "Priority", "Parent ID", "Tags"])
    for task in project.tasks:
        tags = ",".join(tag.name for tag in task.tags)
        writer.writerow([
            task.id, task.title, task.description,
            task.due_date.strftime('%Y-%m-%d') if task.due_date else "",
            task.completed, task.priority, task.parent_id or "", tags
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={project.title}_tasks.csv"}
    )