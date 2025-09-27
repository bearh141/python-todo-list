from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = next(get_db())
        user = db.query(User).filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["is_admin"] = user.is_admin
            flash("Login successful!", "success")

            print(session)
            return redirect(url_for("project.dashboard"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = next(get_db())
        if db.query(User).filter_by(username=username).first():
            flash("Username already taken", "danger")
            return redirect(url_for("auth.register"))

        user = User(username=username)
        user.set_password(password)
        db.add(user)
        db.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("index"))
