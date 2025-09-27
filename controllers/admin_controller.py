from flask import Blueprint, render_template, session, redirect, url_for
from database import get_db
from models.user import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
def admin_dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("index"))

    db = next(get_db())
    users = db.query(User).all()
    return render_template("admin_dashboard.html", users=users)
