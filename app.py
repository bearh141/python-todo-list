from flask import Flask, render_template, session, redirect, url_for
from config import SECRET_KEY
from database import engine, Base
from models import init_db
# from controllers.auth_controller import auth_bp
# from controllers.project_controller import project_bp
# from controllers.task_controller import task_bp
# from controllers.profile_controller import profile_bp
# from controllers.admin_controller import admin_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY  # nên load từ .env

# Khởi tạo DB schema
init_db()

# Đăng ký blueprint
# app.register_blueprint(auth_bp)
# app.register_blueprint(project_bp)
# app.register_blueprint(task_bp)
# app.register_blueprint(profile_bp)
# app.register_blueprint(admin_bp)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('project.dashboard'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)