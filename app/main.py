"""
Main FastAPI application module.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import auth, tasks
from app.core.events import startup_event_handler, shutdown_event_handler


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url="/docs",  # Always enable docs for now
        redoc_url="/redoc",  # Always enable redoc for now
    )

    # Set up CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Set up event handlers
    application.add_event_handler("startup", startup_event_handler(application))
    application.add_event_handler("shutdown", shutdown_event_handler(application))

    # Include routers
    application.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    application.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

    # Future routers (to be implemented)
    # application.include_router(projects.router, prefix="/projects", tags=["Projects"])
    # application.include_router(discussions.router, prefix="/discussions", tags=["Discussions"])
    # application.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])

    @application.get("/", tags=["Status"])
    async def root():
        """
        Root endpoint to check API status.
        """
        return {"status": "online", "environment": settings.ENVIRONMENT}

    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
