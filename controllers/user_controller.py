from sqlalchemy.orm import Session
from models.user import User
from database import get_db

class UserController:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, username: str, email: str, hashed_password: str):
        db_user = User(username=username, email=email, hashed_password=hashed_password)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update_user(self, username: str, email: str):
        db_user = User(username=username, email=email)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def delete_user(self, id):
        db_user = User(id = id)
        return db_user