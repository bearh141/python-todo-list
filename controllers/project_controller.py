from flask import Blueprint, render_template, session, redirect, url_for
from database import get_db
from models.project import Project

project_bp = Blueprint("project", __name__, url_prefix="/project")

@project_bp.route("/")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    projects = db.query(Project).filter_by(user_id=session["user_id"]).all()

    return render_template("project/dashboard.html", projects=projects)
