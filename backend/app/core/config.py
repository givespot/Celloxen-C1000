from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Celloxen Health Portal"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Multi-tenant clinic management system for Celloxen therapies"

    # Security - MUST be set via environment variable
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database - credentials from environment variables
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("DB_USER", "celloxen_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "celloxen_portal")

    @property
    def DATABASE_URL(self) -> str:
        """Build database URL from environment variables"""
        if not self.DB_PASSWORD:
            raise ValueError("DB_PASSWORD environment variable must be set")
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Environment - default to production for safety
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS - only allow production domain by default
    BACKEND_CORS_ORIGINS: List[str] = [
        "https://celloxen.com"
    ]
    
    # Email Configuration (IONOS SMTP)
    SMTP_SERVER: str = "smtp.ionos.co.uk"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@celloxen.com"
    EMAIL_FROM_NAME: str = "Celloxen Health Portal"
    
    # SMS Configuration (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10485760
    UPLOAD_PATH: str = "/var/www/celloxen-portal/uploads"
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Business Settings
    DEFAULT_THERAPY_SESSIONS: int = 20
    ASSESSMENT_VALIDITY_DAYS: int = 365
    SESSION_DURATION_MINUTES: int = 45
    
    # User Roles - 3 Portals Only
    USER_ROLES: Dict[str, str] = {
        "SUPER_ADMIN": "super_admin",
        "CLINIC_USER": "clinic_user",
        "PATIENT": "patient"
    }
    
    # Therapy Domains
    THERAPY_DOMAINS: List[str] = [
        "Diabetics",
        "Chronic Pain", 
        "Anxiety",
        "Energy Rejuvenation"
    ]
    
    # Celloxen Device Codes
    DEVICE_CODES: Dict[str, Dict[str, Any]] = {
        "C-101": {"name": "Circulation & Foot Health", "domain": "Diabetics", "sessions": 18},
        "C-102": {"name": "Metabolic Balance", "domain": "Diabetics", "sessions": 22},
        "C-103": {"name": "Eye Health Support", "domain": "Diabetics", "sessions": 14},
        "C-104": {"name": "Joint Health Support", "domain": "Chronic Pain", "sessions": 14},
        "C-105": {"name": "Heart & Circulation", "domain": "Diabetics", "sessions": 18},
        "C-106": {"name": "Kidney Health Support", "domain": "Diabetics", "sessions": 18},
        "C-107": {"name": "Mental Wellness", "domain": "Anxiety", "sessions": 14},
        "C-108": {"name": "Comprehensive Metabolic", "domain": "Diabetics", "sessions": 22},
    }
    
    # Clinic Settings
    MAX_CLINICS_PER_SUPER_ADMIN: int = 100
    MAX_STAFF_PER_CLINIC: int = 50
    MAX_PATIENTS_PER_CLINIC: int = 10000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
