"""
Email System Configuration
All credentials must be set via environment variables
"""
import os

# IONOS SMTP Settings - from environment
SMTP_SERVER = os.getenv("SMTP_HOST", "smtp.ionos.co.uk")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USER", "health@celloxen.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Required
FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "health@celloxen.com")
FROM_NAME = os.getenv("SMTP_FROM_NAME", "Celloxen Health")

# Database Settings - from environment
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "celloxen_portal")
DB_USER = os.getenv("DB_USER", "celloxen_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")  # Required
