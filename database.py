from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "sqlite:///./todo.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        # Xử lý lỗi SQLAlchemy
        print(f"Lỗi cơ sở dữ liệu: {e}")
        # Bạn có thể raise lại lỗi để xử lý ở tầng cao hơn nếu cần
        raise
    finally:
        # Đảm bảo phiên kết nối luôn được đóng
        db.close()