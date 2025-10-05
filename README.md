# Personal Manager Backend

A modern FastAPI-based backend for the Personal Manager system with MongoDB authentication and Google Calendar integration.

## Features

- **FastAPI REST API**: High-performance async web framework
- **MongoDB Integration**: With secure authentication support
- **Google Calendar Integration**: Real-time sync with Google services
- **JWT Authentication**: Secure token-based authentication
- **Task Management**: CRUD operations for tasks and events
- **Modular Architecture**: Following FastAPI best practices

## Quick Start

### Local Development

1. **Prerequisites**:
   - Python 3.11+
   - MongoDB 4.4+

2. **Installation**:
   ```bash
   git clone https://github.com/yourusername/personal-manager-backend.git
   cd personal-manager-backend
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Start the application:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at http://localhost:8000.

### Docker Deployment

For production deployment using Docker:

1. **Prerequisites**:
   - [Docker](https://www.docker.com/products/docker-desktop/)
   - [Docker Compose](https://docs.docker.com/compose/install/)
   - MongoDB instance (local or cloud)

2. **Setup**:
   ```bash
   # Copy environment template
   cp .env.prod.example .env.prod
   # Edit .env.prod with your production settings
   
   # Deploy using the deployment script
   ./deploy.sh deploy
   ```

3. **Manual Docker Compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up --build
   ```

The containerized API will be available at http://localhost:8000.

## API Documentation

Once the server is running, you can access:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

The application follows a modern architecture with clear separation of concerns:

```
app/
├── main.py               # FastAPI app creation and configuration
├── core/                 # Core modules (config, database, events)
├── api/                  # API endpoints and dependencies
├── schemas/              # Pydantic models for request/response
├── services/             # Business logic
└── integrations/         # External service integrations
```

For more details on the architecture, see [docs/architecture.md](docs/architecture.md).

## Documentation

- [Installation Guide](docs/installation.md)
- [Architecture Overview](docs/architecture.md)
- [Troubleshooting](docs/troubleshooting.md)

## Development

To run the application in development mode with automatic reloading:

```bash
uvicorn app.main:app --reload
```

## Testing

Run the test suite with:

```bash
pytest
```

## License

[MIT](LICENSE)
