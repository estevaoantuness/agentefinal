"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config.settings import settings
from src.api.webhooks import router as webhook_router
from src.database.session import init_db
from src.integrations.scheduler import reminder_scheduler
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Pangeia Agent...")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Load pending reminders
    try:
        reminder_scheduler.load_pending_reminders()
        logger.info("Pending reminders loaded")
    except Exception as e:
        logger.error(f"Failed to load reminders: {e}")

    # Schedule daily Notion sync
    try:
        reminder_scheduler.schedule_daily_sync()
        logger.info("Daily sync scheduled")
    except Exception as e:
        logger.error(f"Failed to schedule daily sync: {e}")

    logger.info(f"Pangeia Agent started on {settings.APP_HOST}:{settings.APP_PORT}")

    yield

    # Shutdown
    logger.info("Shutting down Pangeia Agent...")
    reminder_scheduler.shutdown()
    logger.info("Pangeia Agent stopped")


# Create FastAPI app
app = FastAPI(
    title="Pangeia Task Manager Agent",
    description="Agente inteligente de gestão de tarefas integrado ao WhatsApp",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook_router, tags=["webhooks"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Pangeia Task Manager Agent",
        "version": "1.0.0",
        "status": "running",
        "description": "Agente inteligente de gestão de tarefas da Pangeia"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
