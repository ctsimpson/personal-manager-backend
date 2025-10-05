# Personal Manager Backend Installation Guide

This guide provides step-by-step instructions for setting up the Personal Manager Backend with MongoDB authentication.

## Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Poetry (optional, for dependency management)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/personal-manager-backend.git
cd personal-manager-backend
```

### 2. Set Up a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB

1. Start MongoDB:
   ```bash
   mongod --dbpath /path/to/your/data/directory
   ```

2. Create a MongoDB user with appropriate permissions:
   ```javascript
   // Connect to MongoDB
   mongo

   // Switch to admin database
   use admin

   // Create a user
   db.createUser({
     user: "admin",
     pwd: "your_secure_password",
     roles: [
       { role: "userAdminAnyDatabase", db: "admin" },
       { role: "readWriteAnyDatabase", db: "admin" }
     ]
   })

   // Switch to your project database
   use personal_manager

   // Create a database-specific user (optional)
   db.createUser({
     user: "app_user",
     pwd: "your_app_password",
     roles: [
       { role: "readWrite", db: "personal_manager" }
     ]
   })
   ```

3. Restart MongoDB with authentication enabled:
   ```bash
   mongod --dbpath /path/to/your/data/directory --auth
   ```

### 5. Configure Environment Variables

1. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your MongoDB credentials and other settings:
   ```
   # MongoDB
   MONGODB_HOST=localhost
   MONGODB_PORT=27017
   MONGODB_USER=app_user  # Or admin, depending on your setup
   MONGODB_PASSWORD=your_app_password
   MONGODB_AUTH_SOURCE=admin
   DATABASE_NAME=personal_manager
   ```

### 6. Configure Google Calendar Integration (if needed)

1. Set up Google Cloud project and enable Google Calendar API
2. Create OAuth 2.0 credentials
3. Place the credentials JSON file in the specified location (default: `data/credentials.json`)
4. Update the `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in your `.env` file

## Running the Application

Start the FastAPI application:

```bash
python -m app.main
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

See [troubleshooting.md](./troubleshooting.md) for common issues and solutions.
