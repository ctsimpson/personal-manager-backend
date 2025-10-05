# Project Architecture

This document outlines the architecture of the Personal Manager Backend, explaining the key components and their interactions.

## Overall Structure

The application follows a modern FastAPI architecture with clear separation of concerns:

```
personal-manager-backend/
├── app/                      # Application package
│   ├── main.py               # FastAPI app creation and configuration
│   ├── core/                 # Core modules
│   │   ├── config.py         # Configuration settings
│   │   ├── database.py       # Database connection
│   │   └── events.py         # Event handlers (startup/shutdown)
│   ├── api/                  # API endpoints
│   │   ├── dependencies.py   # Common dependencies
│   │   └── routes/           # Route modules
│   │       ├── auth.py       # Auth routes
│   │       ├── tasks.py      # Task routes
│   │       └── ...
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic models for request/response
│   │   ├── task.py           # Task schemas
│   │   └── ...
│   ├── services/             # Business logic
│   │   ├── auth.py           # Authentication service
│   │   ├── task.py           # Task service
│   │   └── ...
│   └── integrations/         # External service integrations
│       ├── google_calendar/  # Google Calendar integration
│       └── ...
├── docs/                     # Documentation
├── tests/                    # Test suite
└── .env                      # Environment variables (not in version control)
```

## Key Components

### Core

- **config.py**: Configuration management using Pydantic Settings
- **database.py**: MongoDB connection management using Motor
- **events.py**: Application startup/shutdown event handlers

### API Layer

- **routes/**: API endpoints organized by resource
- **dependencies.py**: Shared dependencies for routes, including authentication

### Schema Layer

- **schemas/**: Pydantic models for request/response validation

### Service Layer

- **services/**: Business logic encapsulated in service classes

### Integration Layer

- **integrations/**: External service clients and adapters

## Data Flow

1. **HTTP Request** → API routes
2. Routes use **dependencies** for auth/validation
3. Routes call **services** to execute business logic
4. Services may use **integrations** to communicate with external services
5. Services return data, which is validated by **schemas**
6. API routes return **HTTP Response**

## Authentication

The application uses JWT-based authentication:

1. Client obtains token via `/auth/token` endpoint
2. Token is included in Authorization header for subsequent requests
3. `get_authenticated_user` dependency validates the token

## Database Access

MongoDB is accessed asynchronously using Motor:

1. Connection is established during application startup
2. Services access collections through dependencies
3. Data is stored and retrieved using Motor's async operations

## Configuration

Application settings are managed via:

1. `.env` file containing environment variables
2. `pydantic_settings` for loading and validating settings
3. Settings accessed through the singleton `settings` instance
