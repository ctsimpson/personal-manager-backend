# Migration Guide

This guide provides instructions for migrating from the old project structure to the new FastAPI structure.

## Migration Steps

### 1. Create Basic Directory Structure

First, ensure the new directory structure exists:

```bash
mkdir -p app/{core,api/routes,models,schemas,services,integrations,utils}
mkdir -p tests/{api,services}
```

### 2. Core Setup

Implement core configuration management:
- Create `app/core/config.py` for centralized configuration
- Set up database connection in `app/core/database.py`
- Implement event handlers in `app/core/events.py`

### 3. API Layer Setup

- Create the main FastAPI app in `app/main.py`
- Set up the API router structure in `app/api/routes/`
- Implement common dependencies in `app/api/dependencies.py`

### 4. Models and Schemas

- Separate database models and API schemas
- Move database models to `app/models/`
- Create Pydantic schemas in `app/schemas/`

### 5. Business Logic Layer

- Move business logic from `api/commandline/` to `app/services/`
- Implement proper dependency injection for services

### 6. Integrations

- Move Google Calendar integration from `src/google_calendar/` to `app/integrations/google_calendar/`
- Move Slack integration from `api/slack_routing/` to `app/integrations/slack/`

### 7. Testing

- Update test structure to match the new application structure
- Implement proper test fixtures in `tests/conftest.py`

## Migration Strategy

To ensure a smooth transition:
1. Implement the new structure alongside the existing one
2. Move functionality one module at a time
3. Ensure tests pass after each migration step
4. Once all functionality is migrated, remove the old structure

## Best Practices

1. **Dependency Injection**: Use FastAPI's dependency injection system
2. **Configuration Management**: Use Pydantic Settings for configuration
3. **API Documentation**: Properly document all API endpoints
4. **Error Handling**: Implement proper exception handling
5. **Validation**: Use Pydantic models for validation
6. **Security**: Implement proper authentication and authorization
7. **Testing**: Write comprehensive tests for all components
8. **Async**: Use async/await for I/O-bound operations
