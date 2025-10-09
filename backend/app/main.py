"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import auth_router
from .routes.tournaments import router as tournaments_router
from .routes.leagues import router as leagues_router
from .routes.teams import router as teams_router

# Create FastAPI app
app = FastAPI(
    title="Golf Fantasy League API",
    description="Backend API for fantasy golf league application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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

