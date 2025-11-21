from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from pathlib import Path
import sys
import os

# Add the backend directory to Python path
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Celloxen Health Portal API...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created")
    print("✅ Celloxen Portal API is ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Celloxen Portal API...")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Celloxen Health Portal - Multi-tenant clinic management system",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://celloxen.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "🏥 Celloxen Health Portal API",
        "version": settings.VERSION,
        "status": "operational",
        "docs": f"{settings.API_V1_STR}/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "celloxen-portal-api",
        "version": settings.VERSION
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.DEBUG,
        log_level="info"
    )
