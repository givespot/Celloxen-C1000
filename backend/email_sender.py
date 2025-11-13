"""
Email Sender with Database Logging
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Import from email_config instead of config
from email_config import (
    SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD,
    FROM_EMAIL, FROM_NAME
)
from email_database import log_email


def send_email(to_email: str, subject: str, html_content: str, patient_id=None, email_type="GENERAL") -> tuple:
    """
    Send email via IONOS SMTP with database logging
    
    Returns:
        (success: bool, message: str)
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        # Log success to database
        log_email(patient_id, email_type, to_email, subject, 'SENT')
        
        return (True, "Email sent successfully")
        
    except Exception as e:
        error_msg = f"Email send failed: {str(e)}"
        
        # Log failure to database
        log_email(patient_id, email_type, to_email, subject, 'FAILED', error_msg)
        
        return (False, error_msg)
