import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.sqlite_schema import apply_sqlite_document_patches
from app.db.session import Base, SessionLocal, engine
from app import models  # noqa: F401
from app.routers.api import api_router
from app.services.seed import seed_default_admin
from app.services.seed_documents import seed_demo_documents

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting application: %s", settings.app_name)
    logger.info("📁 Database URL: %s", settings.sqlalchemy_database_url)
    logger.info("🌍 CORS origins: %s", settings.cors_origins)
    
    try:
        logger.info("🗄️ Initializing database...")
        Base.metadata.create_all(bind=engine)
        apply_sqlite_document_patches(engine)
        logger.info("✅ Database tables created successfully")
        
        db = SessionLocal()
        try:
            logger.info("👤 Seeding default admin user...")
            seed_default_admin(db)
            logger.info("✅ Admin user seeded successfully")
            if settings.seed_demo_documents_on_startup:
                logger.info("📚 Seeding demo documents (startup)...")
                stats = seed_demo_documents(db)
                logger.info(
                    "✅ Demo documents: inserted=%s skipped=%s failed=%s",
                    stats["inserted"],
                    stats["skipped"],
                    stats["failed"],
                )
        finally:
            db.close()
    except SQLAlchemyError as exc:
        logger.exception("❌ Database initialization failed: %s", exc)
        raise
    except Exception as exc:
        logger.exception("❌ Unexpected error during startup: %s", exc)
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-Powered Document Knowledge Base API",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")
