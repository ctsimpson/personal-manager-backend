"""
Task-related schemas.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class EventDetails(BaseModel):
    """Event details schema."""

    event_text: str
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    duration: Optional[str] = None
    recurrence: Optional[str] = None
    notes: Optional[str] = None


class TaskBase(BaseModel):
    """Base schema for task data."""

    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: bool = False
    priority: Optional[int] = None


class TaskCreate(TaskBase):
    """Schema for task creation."""

    pass


class TaskUpdate(BaseModel):
    """Schema for task updates."""

    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None
    priority: Optional[int] = None


class TaskInDB(TaskBase):
    """Schema for task stored in database."""

    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class Task(TaskInDB):
    """Schema for task response."""

    pass


class EventRequest(BaseModel):
    """Schema for event requests."""

    event_details: EventDetails
    target_start: Optional[str] = None
    user_id: str


class EventResponse(BaseModel):
    """Schema for event responses."""

    id: str
    summary: str
    description: Optional[str] = None
    start: str
    end: str
    location: Optional[str] = None
    organizer: Optional[str] = None
    attendees: Optional[List[str]] = None
    status: str = "confirmed"
