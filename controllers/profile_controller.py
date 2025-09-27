from flask import Blueprint, render_template, session, redirect, url_for
from database import get_db
from models.user import User

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/")
def view_profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = next(get_db())
    user = db.query(User).get(session["user_id"])
    return render_template("profile.html", user=user)
