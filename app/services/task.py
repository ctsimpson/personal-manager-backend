"""
Task service for business logic related to tasks and events.
"""

from typing import List, Optional
from datetime import datetime
import uuid
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorCollection

from app.schemas.task import EventRequest, EventResponse, Task, TaskCreate, TaskUpdate
from app.integrations.google_calendar.client import GoogleCalendarClient


class TaskService:
    """Service for task-related operations."""

    def __init__(self, tasks_collection: Optional[AsyncIOMotorCollection] = None):
        """
        Initialize the task service.

        Args:
            tasks_collection: MongoDB tasks collection
        """
        self.calendar_client = GoogleCalendarClient()
        self.tasks_collection = tasks_collection

    async def _map_task_from_db(self, task_doc: dict) -> Task:
        """
        Map a task document from the database to a Task schema.

        Args:
            task_doc: Task document from MongoDB

        Returns:
            Task: Task schema
        """
        # Convert MongoDB _id to string id
        task_id = str(task_doc.pop("_id"))

        # Map database document to Task schema
        return Task(id=task_id, **task_doc)

    async def get_tasks(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """
        Get tasks for a user.

        Args:
            user_id: User ID
            skip: Number of tasks to skip (pagination)
            limit: Maximum number of tasks to return (pagination)
            completed: Filter by completion status

        Returns:
            List[Task]: List of tasks
        """
        # Ensure we have a collection
        if not self.tasks_collection:
            return []

        # Build query
        query = {"user_id": user_id}
        if completed is not None:
            query["completed"] = completed

        # Execute query
        cursor = self.tasks_collection.find(query).skip(skip).limit(limit)

        # Convert documents to Task objects
        tasks = []
        async for task_doc in cursor:
            task = await self._map_task_from_db(task_doc)
            tasks.append(task)

        return tasks

    async def create_task(self, user_id: str, task_data: TaskCreate) -> Task:
        """
        Create a new task.

        Args:
            user_id: User ID
            task_data: Task data

        Returns:
            Task: Created task
        """
        # Ensure we have a collection
        if not self.tasks_collection:
            # Generate a task with a random ID as fallback
            now = datetime.now()
            return Task(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title=task_data.title,
                description=task_data.description,
                due_date=task_data.due_date,
                completed=task_data.completed,
                priority=task_data.priority,
                created_at=now,
                updated_at=now,
            )

        # Prepare the task document
        now = datetime.now()
        task_dict = {
            "user_id": user_id,
            "title": task_data.title,
            "created_at": now,
            "updated_at": now,
            "completed": task_data.completed or False,
        }

        # Add optional fields if provided
        if task_data.description:
            task_dict["description"] = task_data.description
        if task_data.due_date:
            task_dict["due_date"] = task_data.due_date
        if task_data.priority is not None:
            task_dict["priority"] = task_data.priority

        # Insert the task
        result = await self.tasks_collection.insert_one(task_dict)

        # Return the task with the generated ID
        return Task(id=str(result.inserted_id), **task_dict)

    async def get_task(self, task_id: str, user_id: str) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: Task ID
            user_id: User ID

        Returns:
            Optional[Task]: Task if found, None otherwise
        """
        # Ensure we have a collection and valid IDs
        if not self.tasks_collection or not task_id or not user_id:
            return None

        try:
            # Query for the task
            task_doc = await self.tasks_collection.find_one(
                {"_id": ObjectId(task_id), "user_id": user_id}
            )

            # Return None if not found
            if not task_doc:
                return None

            # Map to Task schema
            return await self._map_task_from_db(task_doc)

        except Exception as e:
            # Handle invalid ObjectId or other errors
            return None

    async def update_task(
        self, task_id: str, user_id: str, task_update: TaskUpdate
    ) -> Optional[Task]:
        """
        Update a task.

        Args:
            task_id: Task ID
            user_id: User ID
            task_update: Task update data

        Returns:
            Optional[Task]: Updated task if found, None otherwise
        """
        # Ensure we have a collection and valid IDs
        if not self.tasks_collection or not task_id or not user_id:
            return None

        try:
            # Get update data from TaskUpdate model
            update_data = task_update.dict(exclude_unset=True, exclude_none=True)

            # If no updates, just return the current task
            if not update_data:
                return await self.get_task(task_id, user_id)

            # Add updated_at timestamp
            update_data["updated_at"] = datetime.now()

            # Perform the update
            result = await self.tasks_collection.update_one(
                {"_id": ObjectId(task_id), "user_id": user_id}, {"$set": update_data}
            )

            # If task was not found or not updated
            if result.matched_count == 0:
                return None

            # Return the updated task
            return await self.get_task(task_id, user_id)

        except Exception as e:
            # Handle invalid ObjectId or other errors
            return None

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task ID
            user_id: User ID

        Returns:
            bool: True if deleted, False otherwise
        """
        # Ensure we have a collection and valid IDs
        if not self.tasks_collection or not task_id or not user_id:
            return False

        try:
            # Perform the delete operation
            result = await self.tasks_collection.delete_one(
                {"_id": ObjectId(task_id), "user_id": user_id}
            )

            # Return whether a document was deleted
            return result.deleted_count > 0

        except Exception as e:
            # Handle invalid ObjectId or other errors
            return False

    async def list_events(self, event_request: EventRequest) -> List[EventResponse]:
        """
        List events for a user based on request criteria.

        This is the new service implementation of the original TaskListModel.list_events method.

        Args:
            event_request: Event request data with user ID and criteria

        Returns:
            List[EventResponse]: List of events
        """
        # This would integrate with the Google Calendar API
        # For now, we'll provide a simple implementation that mimics the original
        events = await self.fetch_events(event_request)

        processed_events = []
        for event in events:
            # Process event dates and times if needed
            processed_event = EventResponse(
                id=event.get("id", ""),
                summary=event.get("summary", ""),
                description=event.get("description"),
                start=event.get("start", ""),
                end=event.get("end", ""),
                location=event.get("location"),
                organizer=event.get("organizer"),
                attendees=event.get("attendees"),
                status=event.get("status", "confirmed"),
            )
            processed_events.append(processed_event)

        return processed_events

    async def fetch_events(self, event_request: EventRequest) -> List[dict]:
        """
        Fetch events from Google Calendar.

        This is the new service implementation of the original TaskListModel.fetch_events method.

        Args:
            event_request: Event request data with user ID and criteria

        Returns:
            List[dict]: Raw event data from Google Calendar
        """
        # In a real implementation, this would call the Google Calendar API
        # For demonstration, returning mock data
        return [
            {
                "id": "event1",
                "summary": "Team Meeting",
                "description": "Weekly team sync",
                "start": "2025-10-02T10:00:00-07:00",
                "end": "2025-10-02T11:00:00-07:00",
                "location": "Conference Room A",
                "organizer": "manager@example.com",
                "attendees": ["user1@example.com", "user2@example.com"],
                "status": "confirmed",
            },
            {
                "id": "event2",
                "summary": "Project Review",
                "description": "Monthly project status review",
                "start": "2025-10-05T14:00:00-07:00",
                "end": "2025-10-05T15:30:00-07:00",
                "location": "Virtual",
                "organizer": "director@example.com",
                "attendees": ["user1@example.com", "manager@example.com"],
                "status": "confirmed",
            },
        ]
