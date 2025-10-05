"""
Authentication service.

This module provides functions for user authentication and authorization.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

# Simple mock user database for development
# In a real application, this would be replaced with a database query
MOCK_USERS = {
    "testuser": {
        "id": "user1",
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "$2b$12$Ii8wDlnP4JsKJRoQGpuN/e1qKUCzxL9XmCVc1vb10UyZ9.EwQ9wEu",  # "password"
        "is_active": True,
        "is_admin": False,
    },
    "admin": {
        "id": "admin1",
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$2RPNVtBBmLJNM6xNrUeqEOYKpYA9wvAGZlmRoG9.XOPMeWL02V0/i",  # "adminpassword"
        "is_active": True,
        "is_admin": True,
    },
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode JWT token and return user if valid.

    Args:
        token: JWT token

    Returns:
        Optional[Dict[str, Any]]: User data if token is valid, None otherwise
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        # In a real application, this would be a database lookup
        user = MOCK_USERS.get(username)
        if user is None:
            raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception


async def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user with username and password.

    Args:
        username: Username
        password: Password

    Returns:
        Optional[Dict[str, Any]]: User data if authentication successful, None otherwise
    """
    # This is a mock implementation for development
    # In a real application, this would verify the password hash
    user = MOCK_USERS.get(username)
    if not user:
        return None

    # Mock password verification
    # In a real application, use a proper password verification
    if username == "testuser" and password == "password":
        return user
    elif username == "admin" and password == "adminpassword":
        return user

    return None


async def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        str: JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

    return encoded_jwt
