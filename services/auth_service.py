from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from models import User

def register_user(username, password):
    db = next(get_db())
    existing = db.query(User).filter_by(username=username,).first()
    if existing:
        return None
    user = User(
        username=username,
        password=generate_password_hash(password),
        role="user"
    )
    db.add(user)
    db.commit()
    return user

def authenticate_user(username, password):
    db = next(get_db())
    user = db.query(User).filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None
