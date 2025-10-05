"""
Application configuration settings.
"""

from typing import List, Optional, Union, Any
from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.

    All settings can be overridden by environment variables.
    """

    # Core settings
    PROJECT_NAME: str = "Personal Manager Backend"
    PROJECT_DESCRIPTION: str = (
        "Backend API for Personal Manager system with Google Calendar integration"
    )
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_PREFIX: str = ""

    # CORS settings - stored as string, parsed to list
    ALLOWED_ORIGINS_STR: str = (
        "http://localhost:8000,https://29098e308ec4.ngrok-free.app"
    )

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Parse ALLOWED_ORIGINS_STR into a list."""
        if self.ALLOWED_ORIGINS_STR.strip().startswith("["):
            # Handle JSON format
            import json

            try:
                return json.loads(self.ALLOWED_ORIGINS_STR)
            except json.JSONDecodeError:
                pass
        # Handle comma-separated format
        return [
            origin.strip()
            for origin in self.ALLOWED_ORIGINS_STR.split(",")
            if origin.strip()
        ]

    # Security settings
    SECRET_KEY: str = "changeThisInProduction"  # Used for JWT tokens
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database settings
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_USER: Optional[str] = None
    MONGODB_PASSWORD: Optional[str] = None
    MONGODB_AUTH_SOURCE: str = "admin"
    DATABASE_NAME: str = "personal_manager"

    # MongoDB URL - can be provided directly or built from components
    MONGODB_URL: Optional[str] = None

    def get_mongodb_url(self) -> str:
        """
        Get MongoDB connection string, using direct URL if provided or building from components.

        Returns:
            str: MongoDB connection URI
        """
        # If MONGODB_URL is directly provided, use it
        if self.MONGODB_URL:
            return self.MONGODB_URL

        # Otherwise, build from components
        # Basic connection string
        if not self.MONGODB_USER or not self.MONGODB_PASSWORD:
            return f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}"

        # Connection string with authentication
        return (
            f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@"
            f"{self.MONGODB_HOST}:{self.MONGODB_PORT}/"
            f"?authSource={self.MONGODB_AUTH_SOURCE}&authMechanism=DEFAULT"
        )

    # Google API settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CREDENTIALS_FILE: str = "data/credentials.json"

    # Scheduler settings
    SCHEDULER_TIMEZONE: str = "America/Los_Angeles"

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "env_parse_none_str": "None",
        "env_parse_enums": False,
        "extra": "ignore",  # Ignore extra fields like ALLOWED_ORIGINS
    }


# Create settings instance
settings = Settings()
