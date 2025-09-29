from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from database import get_db
from models.task import Task
from datetime import datetime

task_bp = Blueprint("task", __name__, url_prefix="/task")

# Tạo task or sub-task
@task_bp.route("/create/<int:project_id>", methods=["POST"])
def create_task(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    title = request.form.get("title")
    description = request.form.get("description")
    due_date_str = request.form.get("due_date")
    parent_id = request.form.get("parent_id")

    if not title:
        flash("Task title is required.", "error")
        return redirect(url_for("project.view_project", project_id=project_id))
        
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None

    db = next(get_db())
    new_task = Task(
        title=title,
        description=description,
        due_date=due_date,
        project_id=project_id,
        owner_id=session["user_id"],
        parent_id=int(parent_id) if parent_id else None
    )
    db.add(new_task)
    db.commit()
    
    flash("New task added successfully!", "success")
    return redirect(url_for("project.view_project", project_id=project_id))

# Tạo sub-task
@task_bp.route("/create_subtask/<int:task_id>", methods=["GET", "POST"])
def create_subtask(task_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    parent_task = db.query(Task).filter_by(id=task_id, owner_id=session["user_id"]).first()
    if not parent_task:
        flash("Parent task not found.", "error")
        return redirect(url_for("project.dashboard"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        due_date_str = request.form.get("due_date")

        if not title:
            flash("Sub-task title is required.", "error")
            return redirect(url_for("task.create_subtask", task_id=task_id))

        due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None

        new_subtask = Task(
            title=title,
            description=description,
            due_date=due_date,
            project_id=parent_task.project_id,
            owner_id=session["user_id"],
            parent_id=task_id
        )
        db.add(new_subtask)
        db.commit()
        
        flash("New sub-task added successfully!", "success")
        return redirect(url_for("project.view_project", project_id=parent_task.project_id))

    return render_template("task/create_subtask.html", parent_task=parent_task)

@task_bp.route("/toggle/<int:task_id>")
def toggle_complete(task_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    task = db.query(Task).filter_by(id=task_id, owner_id=session["user_id"]).first()

    if task:
        task.completed = not task.completed
        db.commit()
        flash(f"Task '{task.title}' status updated.", "success")
        return redirect(url_for("project.view_project", project_id=task.project_id))
    
    flash("Task not found.", "error")
    return redirect(url_for("project.dashboard"))

# Xóa task
@task_bp.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    task = db.query(Task).filter_by(id=task_id, owner_id=session["user_id"]).first()

    if task:
        project_id = task.project_id
        db.delete(task)
        db.commit()
        flash(f"Task '{task.title}' has been deleted.", "success")
        return redirect(url_for("project.view_project", project_id=project_id))

    flash("Task not found.", "error")
    return redirect(url_for("project.dashboard"))