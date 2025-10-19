"""
Database connection and utility functions.
"""

import logging
import json
from typing import AsyncGenerator, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

# Global database connection
_mongo_client: Optional[AsyncIOMotorClient] = None
_mongo_db: Optional[AsyncIOMotorDatabase] = None


async def get_mongo_client() -> AsyncIOMotorClient:
    """
    Get MongoDB client instance.

    Returns:
        AsyncIOMotorClient: MongoDB client

    Raises:
        ConnectionError: If connection fails
    """
    global _mongo_client

    if _mongo_client is None:
        try:
            mongodb_url = settings.get_mongodb_url()
            # Mask password in logs for security
            safe_url = mongodb_url.split('@')[0].split(':')[0] + ':***@' + mongodb_url.split('@')[1] if '@' in mongodb_url else mongodb_url
            logger.info(f"Connecting to MongoDB at {safe_url}")
            
            _mongo_client = AsyncIOMotorClient(
                mongodb_url,
                serverSelectionTimeoutMS=10000,  # 10 seconds timeout for cloud connections
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
            )

            # Test the connection
            await _mongo_client.admin.command("ping")
            logger.info("Successfully connected to MongoDB")

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionError(f"Could not connect to MongoDB: {e}")

    return _mongo_client


async def get_database() -> AsyncIOMotorDatabase:
    """
    Get database instance.

    Returns:
        AsyncIOMotorDatabase: MongoDB database

    Raises:
        ConnectionError: If connection fails
    """
    global _mongo_db

    if _mongo_db is None:
        client = await get_mongo_client()
        _mongo_db = client[settings.DATABASE_NAME]
        logger.info(f"Using database: {settings.DATABASE_NAME}")

    return _mongo_db


async def close_mongo_connection() -> None:
    """Close MongoDB connection."""
    global _mongo_client

    if _mongo_client:
        logger.info("Closing MongoDB connection")
        _mongo_client.close()
        _mongo_client = None


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Dependency provider for database access.

    Yields:
        AsyncIOMotorDatabase: MongoDB database
    """
    try:
        db = await get_database()
        yield db
    finally:
        # We don't close the connection here because it's a global connection
        # that should be reused across requests. It will be closed when the
        # application shuts down.
        pass
