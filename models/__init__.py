from .user import User
from .project import Project
from .task import Task
from database import Base, engine
from sqlalchemy.exc import SQLAlchemyError

def init_db():
    """Tạo tất cả các bảng đã được định nghĩa trong SQLAlchemy Base và xử lý ngoại lệ."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Cơ sở dữ liệu và tất cả các bảng đã được tạo thành công.")
    except SQLAlchemyError as e:
        print(f"Lỗi khi tạo bảng: {e}")
    except Exception as e:
        print(f"Đã xảy ra lỗi không xác định: {e}")