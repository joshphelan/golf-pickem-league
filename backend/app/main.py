"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import auth_router
from .routes.tournaments import router as tournaments_router
from .routes.leagues import router as leagues_router
from .routes.teams import router as teams_router
from .scheduler import start_scheduler

# Create FastAPI app
app = FastAPI(
    title="Golf Fantasy League API",
    description="Backend API for fantasy golf league application",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tournaments_router)
app.include_router(leagues_router)
app.include_router(teams_router)

# Health check endpoint
@app.get("/")
def root():
    """API root endpoint."""
    return {
        "message": "Golf Fantasy League API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.get("/api/admin/api-usage")
def api_usage():
    """Return current API call tracking stats."""
    from .services.golf_api_service import golf_api
    return golf_api.get_usage_stats()


@app.get("/api/config/public")
def get_public_config():
    """Return public configuration values for the frontend."""
    return {
        "sync_interval_minutes": settings.SYNC_INTERVAL_MINUTES,
        "playing_hours_start": settings.SCORE_SYNC_PLAYING_HOURS_START,
        "playing_hours_end": settings.SCORE_SYNC_PLAYING_HOURS_END,
    }


# Start scheduler on app startup
@app.on_event("startup")
async def startup_event():
    """Start background scheduler on app startup."""
    # Fix stuck tournaments: mark past tournaments as completed
    _correct_stuck_tournaments()

    # Auto-import tournaments if DB is empty (for fresh PR environments)
    if settings.ENABLE_AUTO_SYNC:
        _seed_tournaments_if_empty()

    start_scheduler()


def _seed_tournaments_if_empty():
    """Import tournaments if DB has none (e.g., fresh PR environment)."""
    from .database import get_db
    from .models.tournament import Tournament
    from .scheduler import import_upcoming_tournaments
    import logging

    logger = logging.getLogger(__name__)
    db = next(get_db())
    try:
        count = db.query(Tournament).count()
        if count == 0:
            logger.info("No tournaments found — running initial import for fresh environment...")
            import_upcoming_tournaments()
            logger.info("Initial tournament import complete.")
        else:
            logger.info(f"Database has {count} tournaments — skipping initial import.")
    except Exception as e:
        logger.error(f"Error checking/seeding tournaments: {e}")
    finally:
        db.close()


def _correct_stuck_tournaments():
    """Mark tournaments with end_date > 2 days ago as completed (idempotent)."""
    from datetime import date, timedelta
    from .database import get_db
    from .models.tournament import Tournament
    import logging

    logger = logging.getLogger(__name__)

    db = next(get_db())
    try:
        cutoff = date.today() - timedelta(days=2)
        stuck = db.query(Tournament).filter(
            Tournament.end_date < cutoff,
            Tournament.status != 'completed',
        ).all()

        if stuck:
            for t in stuck:
                logger.info(f"Correcting tournament '{t.name}' status from '{t.status}' to 'completed'")
                t.status = 'completed'
            db.commit()
            logger.info(f"Corrected {len(stuck)} stuck tournament(s)")
    except Exception as e:
        logger.error(f"Error correcting stuck tournaments: {e}")
        db.rollback()
    finally:
        db.close()
