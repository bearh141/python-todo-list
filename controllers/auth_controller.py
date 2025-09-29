from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print(f"Form data: {request.form}")
        username = request.form.get("username")
        password = request.form.get("password")
        print(f"Username: {username}, Password: {password}")

        if not username or not password:
            flash("Username and password are required", "error")
            return redirect(url_for("auth.login"))

        db = next(get_db())
        user = db.query(User).filter_by(username=username).first()
        print(f"User found: {user}")

        if user and user.check_password(password):
            print("Password check passed")
            session["user_id"] = user.id
            session["username"] = user.username
            session["is_admin"] = user.is_admin
            flash("Login successful!", "success")
            print(f"Redirecting to: {'admin.admin_dashboard' if user.is_admin else 'project.dashboard'}")
            if user.is_admin:
                return redirect(url_for("admin.admin_dashboard"))
            return redirect(url_for("project.dashboard"))
        else:
            print("Invalid username or password")
            flash("Invalid username or password", "error")

    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Debug: In dữ liệu form
        print(f"Form data: {request.form}")
        username = request.form.get("username")
        password = request.form.get("password")
        print(f"Username: {username}, Password: {password}")

        if not username or not password:
            flash("Username and password are required", "error")
            return redirect(url_for("auth.register"))

        db = next(get_db())
        if db.query(User).filter_by(username=username).first():
            print(f"Username {username} already taken")
            flash("Username already taken", "error")
            return redirect(url_for("auth.register"))

        user = User(username=username)
        user.set_password(password)
        db.add(user)
        db.commit()
        print(f"User {username} created successfully")
        flash("Account created! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))