"""
Task management routes.
"""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorCollection

from app.api.dependencies import get_authenticated_user, get_tasks_collection
from app.schemas.task import EventRequest, EventResponse, Task, TaskCreate, TaskUpdate
from app.services.task import TaskService

# Create router
router = APIRouter()


@router.get("/", response_model=List[Task])
async def list_tasks(
    user: Annotated[dict, Depends(get_authenticated_user)],
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None,
    tasks_collection: AsyncIOMotorCollection = Depends(get_tasks_collection),
):
    """
    List all tasks for the authenticated user.

    Args:
        user: Authenticated user information
        skip: Number of tasks to skip (pagination)
        limit: Maximum number of tasks to return (pagination)
        completed: Filter by completion status
        tasks_collection: MongoDB tasks collection

    Returns:
        List[Task]: List of tasks
    """
    task_service = TaskService(tasks_collection)
    return await task_service.get_tasks(user["id"], skip, limit, completed)


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    user: Annotated[dict, Depends(get_authenticated_user)],
    tasks_collection: AsyncIOMotorCollection = Depends(get_tasks_collection),
):
    """
    Create a new task for the authenticated user.

    Args:
        task: Task data
        user: Authenticated user information
        tasks_collection: MongoDB tasks collection

    Returns:
        Task: Created task
    """
    task_service = TaskService(tasks_collection)
    return await task_service.create_task(user["id"], task)


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    user: Annotated[dict, Depends(get_authenticated_user)],
    tasks_collection: AsyncIOMotorCollection = Depends(get_tasks_collection),
):
    """
    Get a specific task by ID.

    Args:
        task_id: Task ID
        user: Authenticated user information
        tasks_collection: MongoDB tasks collection

    Returns:
        Task: Task details

    Raises:
        HTTPException: If task not found or not owned by user
    """
    task_service = TaskService(tasks_collection)
    task = await task_service.get_task(task_id, user["id"])

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    user: Annotated[dict, Depends(get_authenticated_user)],
    tasks_collection: AsyncIOMotorCollection = Depends(get_tasks_collection),
):
    """
    Update a specific task by ID.

    Args:
        task_id: Task ID
        task_update: Task update data
        user: Authenticated user information
        tasks_collection: MongoDB tasks collection

    Returns:
        Task: Updated task

    Raises:
        HTTPException: If task not found or not owned by user
    """
    task_service = TaskService(tasks_collection)
    updated_task = await task_service.update_task(task_id, user["id"], task_update)

    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    user: Annotated[dict, Depends(get_authenticated_user)],
    tasks_collection: AsyncIOMotorCollection = Depends(get_tasks_collection),
):
    """
    Delete a specific task by ID.

    Args:
        task_id: Task ID
        user: Authenticated user information
        tasks_collection: MongoDB tasks collection

    Raises:
        HTTPException: If task not found or not owned by user
    """
    task_service = TaskService(tasks_collection)
    success = await task_service.delete_task(task_id, user["id"])

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )


@router.post("/list_events", response_model=List[EventResponse])
async def list_events(
    event_request: EventRequest,
    user: Annotated[dict, Depends(get_authenticated_user)],
    tasks_collection: AsyncIOMotorCollection = Depends(get_tasks_collection),
):
    """
    List events for a user based on request criteria.

    Args:
        event_request: Event request data
        user: Authenticated user information
        tasks_collection: MongoDB tasks collection

    Returns:
        List[EventResponse]: List of events
    """
    task_service = TaskService(tasks_collection)

    # Ensure the user_id in the request matches the authenticated user
    if event_request.user_id != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID in request does not match authenticated user",
        )

    return await task_service.list_events(event_request)
