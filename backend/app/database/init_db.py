from sqlalchemy import text
from app.database.session import engine
from app.database.base import Base
import app.models  # Ensure all models are registered


def init_db():
    Base.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False


if __name__ == "__main__":
    print("Testing connection...")
    if check_db_connection():
        print("Connected! Creating tables...")
        init_db()
        print("Tables initialized successfully!")
    else:
        print("Failed to connect to database.")
