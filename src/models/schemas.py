"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Evolution API Webhook Schemas
class WebhookMessage(BaseModel):
    """Incoming message from Evolution API webhook."""
    key: dict
    message: dict
    messageType: str
    pushName: Optional[str] = None
    participant: Optional[str] = None


class WebhookData(BaseModel):
    """Webhook data payload."""
    event: str
    instance: str
    data: dict


class WebhookPayload(BaseModel):
    """Complete webhook payload from Evolution API."""
    event: str
    instance: str
    data: WebhookData


# Task Schemas
class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: int
    user_id: int
    notion_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    phone_number: str
    name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Category Schemas
class CategoryBase(BaseModel):
    """Base category schema."""
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#808080", regex=r'^#[0-9A-Fa-f]{6}$')


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Reminder Schemas
class ReminderBase(BaseModel):
    """Base reminder schema."""
    task_id: int
    scheduled_time: datetime
    message: Optional[str] = None


class ReminderCreate(ReminderBase):
    """Schema for creating a reminder."""
    pass


class ReminderResponse(ReminderBase):
    """Schema for reminder response."""
    id: int
    user_id: int
    sent: bool
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
