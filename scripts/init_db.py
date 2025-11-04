"""Database initialization script."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.session import init_db, engine
from src.database.models import Base, User, Task, Category, Reminder, ConversationHistory
from src.utils.logger import logger


def main():
    """Initialize database tables."""
    try:
        logger.info("Starting database initialization...")

        # Create all tables
        init_db()

        logger.info("Database tables created successfully!")

        # Print created tables
        print("\n✅ Database initialized successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - tasks")
        print("  - categories")
        print("  - reminders")
        print("  - conversation_history")

        print(f"\nDatabase URL: {engine.url}")
        print("\nYou can now start the application with:")
        print("  uvicorn src.main:app --reload")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
