from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
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


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Content Security Policy - adjust as needed for your frontend
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://celloxen.com; "
            "frame-ancestors 'none';"
        )

        # Strict Transport Security (for HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Celloxen Health Portal API...")

    # Validate required environment variables
    if not settings.SECRET_KEY:
        print("CRITICAL: SECRET_KEY is not set!")
    if not settings.DB_PASSWORD:
        print("CRITICAL: DB_PASSWORD is not set!")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created")
    print("Celloxen Portal API is ready!")

    yield

    # Shutdown
    print("Shutting down Celloxen Portal API...")


# Determine allowed origins based on environment
CORS_ORIGINS = settings.BACKEND_CORS_ORIGINS
if settings.ENVIRONMENT == "development":
    CORS_ORIGINS = ["http://localhost:3000", "https://celloxen.com"]

# Create FastAPI app - disable docs in production
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Celloxen Health Portal - Multi-tenant clinic management system",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.DEBUG else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware - production only allows celloxen.com
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
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
