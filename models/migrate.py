from sqlalchemy import create_engine, MetaData
from datetime import datetime
DATABASE_URL = "sqlite:///./todo.db"  

def migrate():
    try:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        metadata = MetaData()
        metadata.reflect(bind=engine)

        projects = metadata.tables.get("projects")
        if projects is None:
            print("Error: 'projects' table does not exist. Ensure database is initialized.")
        elif "updated_at" not in projects.c:
            print("Adding updated_at column to projects table...")
            with engine.connect() as connection:
                connection.execute("ALTER TABLE projects ADD COLUMN updated_at DATETIME")
                connection.execute(
                    "UPDATE projects SET updated_at = ? WHERE updated_at IS NULL",
                    (datetime.utcnow(),)
                )
                connection.commit()
            print("Added updated_at to projects table.")
        else:
            print("updated_at column already exists in projects table.")

        tasks = metadata.tables.get("tasks")
        if tasks is None:
            print("Error: 'tasks' table does not exist. Ensure database is initialized.")
        elif "updated_at" not in tasks.c:
            print("Adding updated_at column to tasks table...")
            with engine.connect() as connection:
                connection.execute("ALTER TABLE tasks ADD COLUMN updated_at DATETIME")
                connection.execute(
                    "UPDATE tasks SET updated_at = ? WHERE updated_at IS NULL",
                    (datetime.utcnow(),)
                )
                connection.commit()
            print("Added updated_at to tasks table.")
        else:
            print("updated_at column already exists in tasks table.")

        print("Migration completed successfully.")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()