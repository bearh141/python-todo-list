from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from database import get_db
from models.task import Task
from models.tag import Tag
from models.user import User
from models.project import Project
from models.project_share import ProjectShare
from datetime import datetime, timedelta

task_bp = Blueprint("task", __name__, url_prefix="/task")

def parse_tags(tag_input):
    """Parse comma-separated tag input into a list of tag names."""
    return [tag.strip() for tag in tag_input.split(",") if tag.strip()]

def has_project_edit_permission(db, project_id, user_id):
    """Kiểm tra xem user có quyền edit trên project (owner hoặc share role 'editor')"""
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        return False
    if project.owner_id == user_id:
        return True
    share = db.query(ProjectShare).filter_by(project_id=project_id, user_id=user_id).first()
    return share and share.role == 'editor'

@task_bp.route("/create/<int:project_id>", methods=["POST"])
def create_task(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    if not has_project_edit_permission(db, project_id, session["user_id"]):
        flash("You don't have permission to create tasks in this project.", "error")
        return redirect(url_for("project.view_project", project_id=project_id))

    title = request.form.get("title")
    description = request.form.get("description")
    due_date_str = request.form.get("due_date")
    priority = request.form.get("priority")
    parent_id = request.form.get("parent_id")
    tag_input = request.form.get("tags", "")
    tag_names = parse_tags(tag_input) if tag_input else []

    if not title:
        flash("Task title is required.", "error")
        return redirect(url_for("project.view_project", project_id=project_id))
        
    if db.query(Task).filter_by(title=title, project_id=project_id).first():
        flash("Task title already exists in this project.", "error")
        return redirect(url_for("project.view_project", project_id=project_id))

    due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None
    new_task = Task(
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        project_id=project_id,
        owner_id=session["user_id"],
        parent_id=int(parent_id) if parent_id else None
    )

    for tag_name in tag_names:
        tag = db.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        new_task.tags.append(tag)

    db.add(new_task)
    db.commit()
    flash("New task added successfully!", "success")
    return redirect(url_for("project.view_project", project_id=project_id))

@task_bp.route("/create_subtask/<int:task_id>", methods=["GET", "POST"])
def create_subtask(task_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    parent_task = db.query(Task).filter_by(id=task_id).first()
    if not parent_task:
        flash("Parent task not found.", "error")
        return redirect(url_for("project.dashboard"))

    if not has_project_edit_permission(db, parent_task.project_id, session["user_id"]):
        flash("You don't have permission to create subtasks in this project.", "error")
        return redirect(url_for("project.view_project", project_id=parent_task.project_id))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        due_date_str = request.form.get("due_date")
        priority = request.form.get("priority")
        tag_input = request.form.get("tags", "")
        tag_names = parse_tags(tag_input) if tag_input else []

        if not title:
            flash("Sub-task title is required.", "error")
            return render_template("task/create_subtask.html", parent_task=parent_task)

        if db.query(Task).filter_by(title=title, project_id=parent_task.project_id).first():
            flash("Task title already exists in this project.", "error")
            return render_template("task/create_subtask.html", parent_task=parent_task)

        due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None
        new_subtask = Task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            project_id=parent_task.project_id,
            owner_id=session["user_id"],
            parent_id=task_id
        )

        for tag_name in tag_names:
            tag = db.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            new_subtask.tags.append(tag)

        db.add(new_subtask)
        db.commit()
        flash("New sub-task added successfully!", "success")
        return redirect(url_for("project.view_project", project_id=parent_task.project_id))

    return render_template("task/create_subtask.html", parent_task=parent_task)

@task_bp.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    task = db.query(Task).filter_by(id=task_id).first()
    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("project.dashboard"))

    if not has_project_edit_permission(db, task.project_id, session["user_id"]):
        flash("You don't have permission to edit this task.", "error")
        return redirect(url_for("project.view_project", project_id=task.project_id))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        due_date_str = request.form.get("due_date")
        priority = request.form.get("priority")
        tag_input = request.form.get("tags", "")
        tag_names = parse_tags(tag_input) if tag_input else []

        if not title:
            flash("Task title is required.", "error")
            return render_template("task/edit_task.html", task=task, tags_string=','.join(tag.name for tag in task.tags))

        if db.query(Task).filter_by(title=title, project_id=task.project_id).filter(Task.id != task_id).first():
            flash("Task title already exists in this project.", "error")
            return render_template("task/edit_task.html", task=task, tags_string=','.join(tag.name for tag in task.tags))

        due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None
        task.title = title
        task.description = description
        task.due_date = due_date
        task.priority = priority
        task.tags.clear() 
        for tag_name in tag_names:
            tag = db.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            task.tags.append(tag)
        
        db.commit()
        flash("Task updated successfully!", "success")
        return redirect(url_for("project.view_project", project_id=task.project_id))

    # Prepare the tags string for the GET request
    tags_string = ','.join(tag.name for tag in task.tags) if task.tags else ''
    return render_template("task/edit_task.html", task=task, tags_string=tags_string)

def update_subtasks_status(task, status):
    """Cập nhật đệ quy trạng thái hoàn thành của tất cả các sub-task."""
    for subtask in task.subtasks:
        subtask.completed = status
        update_subtasks_status(subtask, status)

@task_bp.route("/toggle/<int:task_id>", methods=["POST"]) 
def toggle_complete(task_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    task = db.query(Task).filter_by(id=task_id).first()
    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("project.dashboard"))

    if not has_project_edit_permission(db, task.project_id, session["user_id"]):
        flash("You don't have permission to update this task.", "error")
        return redirect(url_for("project.view_project", project_id=task.project_id))
    new_status = not task.completed
    task.completed = new_status
    update_subtasks_status(task, new_status)
    
    db.commit()
    flash(f"Task '{task.title}' and its subtasks have been updated.", "success")
    return redirect(url_for("project.view_project", project_id=task.project_id))

@task_bp.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    task = db.query(Task).filter_by(id=task_id).first()
    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("project.dashboard"))

    if not has_project_edit_permission(db, task.project_id, session["user_id"]):
        flash("You don't have permission to delete this task.", "error")
        return redirect(url_for("project.view_project", project_id=task.project_id))

    project_id = task.project_id
    db.delete(task)
    db.commit()
    flash(f"Task '{task.title}' has been deleted.", "success")
    return redirect(url_for("project.view_project", project_id=project_id))

@task_bp.route("/check_reminders")
def check_reminders():
    from app import mail
    from flask_mail import Message

    db = next(get_db())
    tomorrow = datetime.now() + timedelta(days=1)
    tasks = db.query(Task).filter(
        Task.due_date <= tomorrow,
        Task.completed == False,
        Task.reminder_sent == False
    ).all()

    for task in tasks:
        user = db.query(User).filter_by(id=task.owner_id).first()
        if user:
            msg = Message(
                subject=f"Reminder: Task '{task.title}' is due soon",
                recipients=[user.email],
                body=f"Task '{task.title}' in project '{task.project.title}' is due on {task.due_date.strftime('%Y-%m-%d')}. Please complete it soon!"
            )
            mail.send(msg)
            task.reminder_sent = True

    db.commit()
    return "Reminders checked and sent."