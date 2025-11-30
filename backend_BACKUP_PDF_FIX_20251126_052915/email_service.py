#!/usr/bin/env python3
"""
Email Service for Celloxen Patient Portal
Handles all patient email notifications
"""

import os
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/var/www/.env')

# SMTP Configuration from environment
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.ionos.co.uk")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "health@celloxen.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "Kuwait1000$$")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "health@celloxen.com")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Celloxen Health Portal")

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "celloxen_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "CelloxenSecure2025")
DB_NAME = os.getenv("DB_NAME", "celloxen_portal")

print(f"SMTP Config: {SMTP_HOST}:{SMTP_PORT}, User: {SMTP_USER}")


async def send_email(to_email: str, subject: str, html_content: str, patient_id: int = None, email_type: str = "notification"):
    """
    Send email using IONOS SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        patient_id: Patient ID for logging
        email_type: Type of email (welcome, password_reset, report_ready, etc.)
    
    Returns:
        bool: True if sent successfully
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = subject
        
        # Attach HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        print(f"Attempting to send email to {to_email} via {SMTP_HOST}:{SMTP_PORT}")
        
        # Send via IONOS SMTP
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            start_tls=True,
            timeout=30
        )
        
        # Log success
        await log_email(patient_id, email_type, to_email, subject, "SENT")
        
        print(f"✅ Email sent to {to_email}: {subject}")
        return True
        
    except Exception as e:
        print(f"❌ Email send failed to {to_email}: {str(e)}")
        import traceback
        traceback.print_exc()
        await log_email(patient_id, email_type, to_email, subject, "FAILED", str(e))
        return False


async def log_email(patient_id: int, email_type: str, sent_to: str, subject: str, status: str, error: str = None):
    """Log email to database"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        
        await conn.execute("""
            INSERT INTO email_logs (patient_id, email_type, sent_to_email, subject, status, error_message)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, patient_id, email_type, sent_to, subject, status, error)
        
        await conn.close()
    except Exception as e:
        print(f"Email log error: {str(e)}")


# ============================================================================
# EMAIL TEMPLATES
# ============================================================================

def get_email_base_template(content: str) -> str:
    """Base email template with Celloxen branding"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background-color: #f1f5f9;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 700;
        }}
        .content {{
            padding: 30px;
            color: #334155;
            line-height: 1.6;
        }}
        .button {{
            display: inline-block;
            background: #1e3a5f;
            color: white !important;
            padding: 14px 28px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 20px 0;
        }}
        .footer {{
            background: #f8fafc;
            padding: 20px 30px;
            text-align: center;
            color: #64748b;
            font-size: 12px;
        }}
        .info-box {{
            background: #e0f2fe;
            border-left: 4px solid #0284c7;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Celloxen Health Portal</h1>
        </div>
        <div class="content">
            {content}
        </div>
        <div class="footer">
            <p><strong>Aberdeen Wellness Centre</strong></p>
            <p>This is an automated email from Celloxen Health Portal. Please do not reply to this email.</p>
            <p style="margin-top: 15px;">Need help? Contact us at <a href="mailto:health@celloxen.com">health@celloxen.com</a></p>
        </div>
    </div>
</body>
</html>
    """


async def send_welcome_email(patient_email: str, patient_name: str, patient_id: int, temporary_password: str = None):
    """Send welcome email to new patient"""
    content = f"""
        <h2>Welcome to Celloxen Health Portal! 👋</h2>
        <p>Dear {patient_name},</p>
        <p>Your patient account has been created at Aberdeen Wellness Centre. You can now access your health reports and appointments online.</p>
        
        <div class="info-box">
            <strong>Your Login Details:</strong><br>
            Email: {patient_email}<br>
            {"Password: " + temporary_password if temporary_password else "Password: (Set by staff)"}
        </div>
        
        <p style="text-align: center;">
            <a href="http://celloxen.com/patient_portal.html" class="button">Access Patient Portal</a>
        </p>
        
        <p><strong>What you can do:</strong></p>
        <ul>
            <li>View your iridology analysis reports</li>
            <li>Check upcoming appointments</li>
            <li>Update your profile information</li>
            <li>Change your password</li>
        </ul>
        
        <p>If you have any questions, please contact our office.</p>
        <p>Best regards,<br><strong>Aberdeen Wellness Centre Team</strong></p>
    """
    
    html = get_email_base_template(content)
    subject = "Welcome to Celloxen Health Portal"
    
    return await send_email(patient_email, subject, html, patient_id, "welcome")


async def send_password_reset_email(patient_email: str, patient_name: str, patient_id: int, reset_token: str):
    """Send password reset email"""
    reset_link = f"http://celloxen.com/patient_portal.html?reset_token={reset_token}"
    
    content = f"""
        <h2>Password Reset Request 🔒</h2>
        <p>Dear {patient_name},</p>
        <p>We received a request to reset your password for your Celloxen patient account.</p>
        
        <p style="text-align: center;">
            <a href="{reset_link}" class="button">Reset Your Password</a>
        </p>
        
        <div class="info-box">
            <strong>⏰ This link will expire in 1 hour</strong><br>
            For your security, please reset your password as soon as possible.
        </div>
        
        <p><strong>If you didn't request this:</strong><br>
        If you didn't request a password reset, please ignore this email or contact us if you have concerns.</p>
        
        <p>Best regards,<br><strong>Aberdeen Wellness Centre Team</strong></p>
    """
    
    html = get_email_base_template(content)
    subject = "Password Reset - Celloxen Health Portal"
    
    return await send_email(patient_email, subject, html, patient_id, "password_reset")


async def send_report_ready_email(patient_email: str, patient_name: str, patient_id: int, report_number: str):
    """Send notification when new report is ready"""
    portal_link = "http://celloxen.com/patient_portal.html"
    
    content = f"""
        <h2>New Report Available 📄</h2>
        <p>Dear {patient_name},</p>
        <p>Good news! Your iridology analysis report is now ready to view.</p>
        
        <div class="info-box">
            <strong>Report Details:</strong><br>
            Report Number: {report_number}<br>
            Date: {datetime.now().strftime('%d %B %Y')}
        </div>
        
        <p style="text-align: center;">
            <a href="{portal_link}" class="button">View Your Report</a>
        </p>
        
        <p><strong>What's in your report:</strong></p>
        <ul>
            <li>Complete iridology analysis</li>
            <li>Constitutional type assessment</li>
            <li>Detailed findings and recommendations</li>
            <li>Downloadable PDF version</li>
        </ul>
        
        <p>Log in to your patient portal to view your complete report and analysis.</p>
        <p>Best regards,<br><strong>Aberdeen Wellness Centre Team</strong></p>
    """
    
    html = get_email_base_template(content)
    subject = f"Your Report is Ready - {report_number}"
    
    return await send_email(patient_email, subject, html, patient_id, "report_ready")


async def send_appointment_reminder_email(patient_email: str, patient_name: str, patient_id: int, 
                                         appointment_date: str, appointment_time: str, practitioner_name: str):
    """Send appointment reminder email"""
    content = f"""
        <h2>Appointment Reminder 📅</h2>
        <p>Dear {patient_name},</p>
        <p>This is a friendly reminder about your upcoming appointment at Aberdeen Wellness Centre.</p>
        
        <div class="info-box">
            <strong>Appointment Details:</strong><br>
            Date: {appointment_date}<br>
            Time: {appointment_time}<br>
            Practitioner: {practitioner_name}<br>
            Location: Aberdeen Wellness Centre
        </div>
        
        <p><strong>Please remember:</strong></p>
        <ul>
            <li>Arrive 10 minutes early</li>
            <li>Bring any relevant medical records</li>
            <li>Contact us if you need to reschedule</li>
        </ul>
        
        <p style="text-align: center;">
            <a href="http://celloxen.com/patient_portal.html" class="button">View in Portal</a>
        </p>
        
        <p>We look forward to seeing you!</p>
        <p>Best regards,<br><strong>Aberdeen Wellness Centre Team</strong></p>
    """
    
    html = get_email_base_template(content)
    subject = f"Appointment Reminder - {appointment_date}"
    
    return await send_email(patient_email, subject, html, patient_id, "appointment_reminder")


async def send_appointment_confirmation_email(patient_email: str, patient_name: str, patient_id: int,
                                              appointment_date: str, appointment_time: str, appointment_type: str):
    """Send appointment confirmation email"""
    content = f"""
        <h2>Appointment Confirmed ✅</h2>
        <p>Dear {patient_name},</p>
        <p>Your appointment at Aberdeen Wellness Centre has been confirmed!</p>
        
        <div class="info-box">
            <strong>Appointment Details:</strong><br>
            Date: {appointment_date}<br>
            Time: {appointment_time}<br>
            Type: {appointment_type}<br>
            Location: Aberdeen Wellness Centre
        </div>
        
        <p style="text-align: center;">
            <a href="http://celloxen.com/patient_portal.html" class="button">Manage Appointments</a>
        </p>
        
        <p><strong>What to expect:</strong></p>
        <ul>
            <li>Comprehensive health assessment</li>
            <li>Professional iridology analysis</li>
            <li>Personalized recommendations</li>
        </ul>
        
        <p>Need to reschedule? Contact us or use the patient portal.</p>
        <p>Best regards,<br><strong>Aberdeen Wellness Centre Team</strong></p>
    """
    
    html = get_email_base_template(content)
    subject = "Appointment Confirmed"
    
    return await send_email(patient_email, subject, html, patient_id, "appointment_confirmation")


# Test function
async def test_email_system():
    """Test the email system"""
    # Use a real email address for testing
    test_email = input("Enter test email address (or press Enter for default): ").strip()
    if not test_email:
        test_email = "abidkhan484@gmail.com"  # Change this to your email
    
    print(f"\nSending test email to: {test_email}")
    
    result = await send_welcome_email(
        test_email,
        "Test Patient",
        22,
        "TestPassword123!"
    )
    
    if result:
        print("\n✅ Email system test successful!")
        print(f"Check {test_email} for the welcome email")
    else:
        print("\n❌ Email system test failed!")
    
    return result


if __name__ == "__main__":
    # Test the email system
    asyncio.run(test_email_system())
