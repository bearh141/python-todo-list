from datetime import datetime
from flask import Flask, render_template, session
from config import SECRET_KEY
from database import engine, Base
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

init_db()

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)