"""
Common dependencies for API routes.

This module provides dependency functions for FastAPI dependency injection.
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.core.config import settings
from app.core.database import get_db
from app.services.auth import get_current_user

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# Database dependencies
async def get_tasks_collection(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> AsyncIOMotorCollection:
    """
    Dependency to get the tasks collection.

    Args:
        db: MongoDB database instance

    Returns:
        AsyncIOMotorCollection: Tasks collection
    """
    return db.tasks


async def get_projects_collection(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> AsyncIOMotorCollection:
    """
    Dependency to get the projects collection.

    Args:
        db: MongoDB database instance

    Returns:
        AsyncIOMotorCollection: Projects collection
    """
    return db.projects


async def get_organizations_collection(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> AsyncIOMotorCollection:
    """
    Dependency to get the organizations collection.

    Args:
        db: MongoDB database instance

    Returns:
        AsyncIOMotorCollection: Organizations collection
    """
    return db.organizations


async def get_discussions_collection(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> AsyncIOMotorCollection:
    """
    Dependency to get the discussions collection.

    Args:
        db: MongoDB database instance

    Returns:
        AsyncIOMotorCollection: Discussions collection
    """
    return db.discussions


# Authentication dependencies
async def get_authenticated_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Dependency to verify and return the authenticated user.

    Args:
        token: JWT token from request

    Returns:
        dict: User information

    Raises:
        HTTPException: If authentication fails
    """
    user = await get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_admin_user(user: Annotated[dict, Depends(get_authenticated_user)]):
    """
    Dependency to verify the user has admin privileges.

    Args:
        user: Authenticated user information

    Returns:
        dict: Admin user information

    Raises:
        HTTPException: If user is not an admin
    """
    if not user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return user
