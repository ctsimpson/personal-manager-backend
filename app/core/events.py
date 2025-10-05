"""
Application event handlers.

This module contains event handlers for application startup and shutdown.
"""

from typing import Callable
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.core.database import get_database, close_mongo_connection

# Global scheduler instance
scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)


def startup_event_handler(app: FastAPI) -> Callable:
    """
    FastAPI startup event handler.

    Args:
        app: FastAPI application instance

    Returns:
        Callable: Startup handler function
    """

    async def startup() -> None:
        """
        Initialize services on application startup.
        """
        # Start the scheduler
        if not scheduler.running:
            scheduler.start()

            # Add scheduled jobs
            # Example: Add a midnight refresh job
            # @scheduler.scheduled_job('cron', hour=0, minute=0)
            # async def midnight_refresh():
            #     # Perform midnight refresh tasks
            #     pass

        # Initialize database connection
        await get_database()  # This initializes the MongoDB connection

        # Initialize external services

    return startup


def shutdown_event_handler(app: FastAPI) -> Callable:
    """
    FastAPI shutdown event handler.

    Args:
        app: FastAPI application instance

    Returns:
        Callable: Shutdown handler function
    """

    async def shutdown() -> None:
        """
        Clean up resources on application shutdown.
        """
        # Shutdown the scheduler
        if scheduler.running:
            scheduler.shutdown()

        # Close database connection
        await close_mongo_connection()

        # Clean up other resources

    return shutdown
