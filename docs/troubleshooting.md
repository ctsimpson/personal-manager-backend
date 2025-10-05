# Troubleshooting Guide

This document provides solutions for common issues that you might encounter when setting up and running the Personal Manager Backend.

## MongoDB and BSON Issues

### Issue: `ImportError: cannot import name 'SON' from 'bson'`

This error occurs when the standalone `bson` package is installed alongside `pymongo`. The `pymongo` package includes its own version of `bson`, which is incompatible with the standalone `bson` package.

#### Solution:

1. Uninstall the standalone `bson` package:
   ```bash
   pip uninstall bson
   ```

2. Make sure you're using the BSON module from pymongo:
   ```python
   # Instead of
   from bson import ObjectId
   
   # Use
   from pymongo.bson import ObjectId
   ```

3. If you see this error even after uninstalling the standalone `bson` package, you may need to reinstall pymongo:
   ```bash
   pip uninstall pymongo
   pip install pymongo>=4.0.0
   ```

### Issue: MongoDB Connection Problems

If you're having trouble connecting to MongoDB, try these steps:

1. Verify that MongoDB is running:
   ```bash
   # On macOS/Linux
   ps aux | grep mongod
   
   # On Windows
   tasklist | findstr mongod
   ```

2. Check connection string format:
   - Without authentication: `mongodb://localhost:27017`
   - With authentication: `mongodb://username:password@localhost:27017/?authSource=admin&authMechanism=DEFAULT`

3. Try connecting using the MongoDB CLI to verify credentials:
   ```bash
   mongo -u <username> -p <password> --authenticationDatabase admin
   ```

## Pydantic Settings Issues

### Issue: `pydantic.errors.PydanticImportError: BaseSettings has been moved to pydantic-settings`

This error occurs when using Pydantic v2 but importing `BaseSettings` from the wrong location.

#### Solution:

1. Install the `pydantic-settings` package:
   ```bash
   pip install pydantic-settings>=2.0.0
   ```

2. Update imports to use the correct package:
   ```python
   # Instead of
   from pydantic import BaseSettings
   
   # Use
   from pydantic_settings import BaseSettings
   ```

### Issue: JSON decode error in settings

If you see a JSON decode error related to settings:

1. Check that any list/dictionary values in your `.env` file are properly formatted. The application supports both JSON and comma-separated formats:
   ```
   # JSON format (both work)
   ALLOWED_ORIGINS_STR=["http://localhost:8000","https://example.com"]
   
   # Comma-separated format (both work)
   ALLOWED_ORIGINS_STR=http://localhost:8000,https://example.com
   ```

2. If you're using environment variables with complex types, ensure they're properly JSON-encoded.

## JWT Authentication Issues

### Issue: JWT token validation fails

If you're having issues with JWT token validation:

1. Check that the `SECRET_KEY` is consistent and sufficiently secure
2. Verify token expiration time is appropriate
3. Ensure the token is being passed correctly in the Authorization header

## General Troubleshooting

### Environment Variables

If you suspect environment variable issues:

1. Ensure you have a `.env` file in the project root
2. Check that it contains all required variables from `.env.example`
3. Verify the format of complex variables (lists, dictionaries) as proper JSON

### Clean Installation

If all else fails, try a clean installation:

```bash
# Create a fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # On Windows: fresh_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
