"""
Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.data_sources.data_service import DataService


# Global data service instance
data_service: DataService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global data_service
    
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.app_env}")
    
    # Initialize data service
    try:
        data_service = DataService(settings)
        await data_service.initialize()
        print("Data service initialized successfully")
    except Exception as e:
        print(f"Warning: Failed to initialize data service: {str(e)}")
        print("Application will continue but data features may be limited")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    if data_service:
        try:
            await data_service.close()
            print("Data service closed successfully")
        except Exception as e:
            print(f"Error closing data service: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Options Trading Dashboard API",
    version=settings.app_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api.routes import router
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "data_service": "connected" if data_service and data_service.is_connected() else "disconnected"
    }
    
    # Add cache stats if available
    if data_service and data_service.is_connected():
        try:
            cache_stats = await data_service.get_cache_stats()
            status["cache_stats"] = cache_stats
        except Exception as e:
            status["cache_stats"] = {"error": str(e)}
    
    return status


def get_data_service() -> DataService:
    """Get the global data service instance"""
    return data_service