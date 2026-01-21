"""
One-time PostgreSQL table initialization script for AURA System.
Creates tables from SQLAlchemy models.
"""

from app.db.postgres_database import engine
from app.db.postgres_models import Base


def init_postgres_tables():
    print("🛠️ Creating PostgreSQL tables (if not exist)...")
    Base.metadata.create_all(bind=engine)
    print("✅ PostgreSQL tables ready.")


if __name__ == "__main__":
    init_postgres_tables()
