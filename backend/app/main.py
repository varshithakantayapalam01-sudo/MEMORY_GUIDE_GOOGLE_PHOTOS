from __future__ import annotations
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routes import health, sessions, images
from app.services import analytics_db, library_service, upload_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("memory_guide.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Starting Memory Guide API...")

    # 1. Initialize SQLite Database
    try:
        analytics_db.init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise e

    # 2. Ensure Temp Upload Directory exists
    try:
        os.makedirs(settings.TEMP_UPLOAD_DIR, exist_ok=True)
        logger.info(f"Temporary upload directory ready at: {os.path.abspath(settings.TEMP_UPLOAD_DIR)}")
    except Exception as e:
        logger.error(f"Failed to create temporary upload directory: {e}")
        raise e

    # 3. Expiration Cleanup for inactive research sessions
    try:
        cleaned = upload_service.cleanup_expired_research_sessions(inactivity_hours=2.0)
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired research session upload directories.")
    except Exception as e:
        logger.warning(f"Error during startup expired session cleanup: {e}")

    yield

    # Shutdown actions
    logger.info("Shutting down Memory Guide API...")


app = FastAPI(
    title="Memory Guide API",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS - allow all origins so public Vercel deployment can query and upload
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static route for Demo Mode photos
demo_photos_dir = os.path.abspath(library_service.DEMO_PHOTOS_DIR)
if os.path.exists(demo_photos_dir):
    app.mount("/images/demo-photos", StaticFiles(directory=demo_photos_dir), name="demo-photos")

# Include API Routers under /api/v1
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(sessions.router, prefix="/api/v1", tags=["Sessions"])
app.include_router(images.router, prefix="/api/v1", tags=["Images"])
