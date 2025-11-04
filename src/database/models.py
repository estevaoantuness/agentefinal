"""SQLAlchemy database models."""
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean,
    ForeignKey, Text, Enum, Float
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.database.session import Base


class TaskStatus(str, enum.Enum):
    """Task status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """Task priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100))
    notion_token = Column(String(200), nullable=True)
    notion_database_id = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.phone_number}>"


class Category(Base):
    """Category model for organizing tasks."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    color = Column(String(7), default="#808080")  # Hex color
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="categories")
    tasks = relationship("Task", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


class Task(Base):
    """Task model."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)

    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Notion sync
    notion_id = Column(String(200), unique=True, nullable=True, index=True)
    last_synced_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
    reminders = relationship("Reminder", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task {self.title} ({self.status})>"


class Reminder(Base):
    """Reminder model for task notifications."""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    scheduled_time = Column(DateTime, nullable=False)
    message = Column(Text, nullable=True)
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="reminders")
    user = relationship("User", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder for Task {self.task_id} at {self.scheduled_time}>"


class ConversationHistory(Base):
    """Store conversation history for LangChain memory."""
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phone_number = Column(String(20), index=True, nullable=False)

    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ConversationHistory {self.role}: {self.content[:50]}>"
