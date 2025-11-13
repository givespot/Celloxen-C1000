"""
Email Sender - WORKING VERSION
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import *


def send_email(to_email: str, subject: str, html_content: str) -> tuple:
    """
    Send email via IONOS SMTP
    
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
        
        return (True, "Email sent successfully")
        
    except Exception as e:
        return (False, f"Email send failed: {str(e)}")


if __name__ == "__main__":
    # Test
    print("Testing final configuration...")
    
    test_html = f"""
    <html>
    <body style="font-family: Arial; padding: 20px;">
        <h2 style="color: #28a745;">✅ Email System Ready!</h2>
        <p>The Celloxen Email System is now operational.</p>
        <p>Sent: {datetime.now()}</p>
    </body>
    </html>
    """
    
    success, message = send_email(
        to_email="health@celloxen.com",
        subject="Celloxen Email System - Ready",
        html_content=test_html
    )
    
    if success:
        print("✅ EMAIL SYSTEM READY!")
    else:
        print(f"❌ FAILED: {message}")
