from datetime import datetime
from flask import Flask, render_template, session
from flask_mail import Mail
from config import SECRET_KEY
from sqlalchemy import create_engine, MetaData
from database import Base, get_db
from models import init_db
from controllers.auth_controller import auth_bp
from controllers.project_controller import project_bp
from controllers.task_controller import task_bp
from controllers.profile_controller import profile_bp
from controllers.admin_controller import admin_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False 
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  
app.config['MAIL_PASSWORD'] = 'your-app-password'     
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'

mail = Mail(app)

DATABASE_URL = "sqlite:///todo.db"  
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def migrate_database():
    try:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        projects = metadata.tables.get("projects")
        if projects is None:
            print("Error: 'projects' table does not exist. Ensure database is initialized.")
            return
        if "updated_at" not in projects.c:
            print("Adding updated_at column to projects table...")
            with engine.connect() as connection:
                connection.execute("ALTER TABLE projects ADD COLUMN updated_at DATETIME")
                connection.execute(
                    "UPDATE projects SET updated_at = ? WHERE updated_at IS NULL",
                    (datetime.utcnow(),)
                )
                connection.commit()
            print("Migration completed successfully.")
        else:
            print("updated_at column already exists.")
        users = metadata.tables.get("users")
        if users is None:
            print("Error: 'users' table does not exist.")
            return
        if "avatar_url" not in users.c:
            print("Adding avatar_url column to users table...")
            with engine.connect() as connection:
                connection.execute("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(200)")
                connection.commit()
        if "theme" not in users.c:
            print("Adding theme column to users table...")
            with engine.connect() as connection:
                connection.execute("ALTER TABLE users ADD COLUMN theme VARCHAR(20) DEFAULT 'light'")
                connection.commit()
        tasks = metadata.tables.get("tasks")
        if tasks is None:
            print("Error: 'tasks' table does not exist.")
            return
        if "owner_id" not in tasks.c:
            print("Adding owner_id column to tasks table...")
            with engine.connect() as connection:
                connection.execute("ALTER TABLE tasks ADD COLUMN owner_id INTEGER")
                connection.commit()
    except Exception as e:
        print(f"Error during migration: {e}")

init_db()
migrate_database()
app.register_blueprint(auth_bp)
app.register_blueprint(project_bp)
app.register_blueprint(task_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug-session')
def debug_session():
    return str(dict(session))

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

from flask import send_from_directory
from models.user import User
from utils import allowed_file, UPLOAD_FOLDER

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads/avatars/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.before_request
def apply_user_theme():
    if 'user_id' in session:
        db = next(get_db())
        user = db.query(User).get(session['user_id'])
        session['theme'] = user.theme if user else 'light'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
