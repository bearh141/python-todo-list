from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from database import get_db
from models.user import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Dashboard quản lý user
@admin_bp.route("/")
def admin_dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("index"))

    db = next(get_db())
    users = db.query(User).all()
    return render_template("admin/dashboard.html", users=users)


# Edit user (chỉ đổi username hoặc quyền admin)
@admin_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if not session.get("is_admin"):
        return redirect(url_for("index"))

    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()

    if not user:
        flash("User not found", "error")
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "POST":
        user.username = request.form.get("username")
        user.is_admin = True if request.form.get("is_admin") == "1" else False
        db.commit()
        flash("User updated successfully!", "success")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("admin/edit_user.html", user=user)


# Delete user
@admin_bp.route("/delete/<int:user_id>")
def delete_user(user_id):
    if not session.get("is_admin"):
        return redirect(url_for("index"))

    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        db.delete(user)
        db.commit()
        flash("User deleted successfully!", "success")

    return redirect(url_for("admin.admin_dashboard"))

# Create new user
@admin_bp.route("/create", methods=["GET", "POST"])
def create_user():
    if not session.get("is_admin"):
        return redirect(url_for("index"))

    db = next(get_db())

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        is_admin = True if request.form.get("is_admin") == "1" else False

        if not username or not password:
            flash("Username and password are required", "error")
            return redirect(url_for("admin.create_user"))

        # Kiểm tra trùng username
        existing = db.query(User).filter_by(username=username).first()
        if existing:
            flash("Username already exists!", "error")
            return redirect(url_for("admin.create_user"))

        # Tạo user mới
        new_user = User(username=username, is_admin=is_admin)
        new_user.set_password(password)
        
        db.add(new_user)
        db.commit()
        flash("User created successfully!", "success")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("admin/create_user.html")
