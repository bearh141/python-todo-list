from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from database import get_db
from models.user import User
from models.project import Project
from models.task import Task
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os
from utils import allowed_file, UPLOAD_FOLDER
import uuid

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/")
def view_profile():
    if "user_id" not in session:
        flash("Please log in to view your profile.", "info")
        return redirect(url_for("auth.login"))

    try:
        db = next(get_db())
        user = db.query(User).get(session["user_id"])
        if not user:
            flash("User not found. Please log in again.", "error")
            session.clear()
            return redirect(url_for("auth.login"))
        project_count = db.query(func.count(Project.id)).filter(Project.owner_id == user.id).scalar() or 0
        task_count = db.query(func.count(Task.id)).filter(Task.owner_id == user.id).scalar() or 0
        completed_tasks = db.query(func.count(Task.id)).filter(Task.owner_id == user.id, Task.completed == True).scalar() or 0

        return render_template(
            "profile.html",
            user=user,
            project_count=project_count,
            task_count=task_count,
            completed_tasks=completed_tasks
        )
    except Exception as e:
        flash(f"Error loading profile: {str(e)}", "error")
        return redirect(url_for("auth.login"))

@profile_bp.route("/edit", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        flash("Please log in to edit your profile.", "info")
        return redirect(url_for("auth.login"))

    try:
        db = next(get_db())
        user = db.query(User).get(session["user_id"])
        if not user:
            flash("User not found. Please log in again.", "error")
            session.clear()
            return redirect(url_for("auth.login"))

        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            theme = request.form.get("theme")
            if username and username != user.username:
                if db.query(User).filter_by(username=username).first():
                    flash("Username already taken.", "error")
                    return render_template("profile_edit.html", user=user)
                user.username = username
                session["username"] = username
            if email:
                user.email = email
            if password:
                user.set_password(password)

            valid_themes = ["light", "dark"]
            if theme in valid_themes:
                user.theme = theme
                session["theme"] = theme
            else:
                flash("Invalid theme selected.", "error")
                return render_template("profile_edit.html", user=user)

            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and allowed_file(file.filename):
                    ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
                    filename = f"avatar_{user.id}_{uuid.uuid4().hex}.{ext}"
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    user.avatar_url = url_for('uploaded_file', filename=filename, _external=False)

            db.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile.view_profile"))

        return render_template("profile_edit.html", user=user)
    except Exception as e:
        flash(f"Error updating profile: {str(e)}", "error")
        return render_template("profile_edit.html", user=user)