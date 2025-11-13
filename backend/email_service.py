"""
Celloxen Health Portal - Email Service
Handles all email communications using IONOS SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# IONOS SMTP Configuration
SMTP_SERVER = "smtp.ionos.com"
SMTP_PORT = 587
SMTP_USERNAME = "noreply@celloxen.com"
SMTP_PASSWORD = "Kuwait1000$$"
FROM_EMAIL = "noreply@celloxen.com"
FROM_NAME = "Celloxen Health"

# Email Templates
EMAIL_TEMPLATES = {
    "INVITATION": {
        "subject": "Welcome to Your Wellness Journey with Celloxen",
        "template": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ background: #333; color: #fff; padding: 20px; text-align: center; font-size: 12px; border-radius: 0 0 10px 10px; }}
        .disclaimer {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Celloxen Health</h1>
            <h2>Welcome to Your Wellness Journey!</h2>
        </div>
        <div class="content">
            <p>Dear {patient_name},</p>
            
            <p>Welcome to Celloxen Health! We're excited to support you on your wellness journey.</p>
            
            <p>To prepare for your visit, please complete your wellness profile by clicking the button below:</p>
            
            <div style="text-align: center;">
                <a href="{registration_link}" class="button">Create Your Account</a>
            </div>
            
            <p>This secure link will:</p>
            <ul>
                <li>✓ Create your personal account</li>
                <li>✓ Guide you through a wellness questionnaire</li>
                <li>✓ Save your information securely</li>
            </ul>
            
            <p>The process takes about 15-20 minutes and can be done from any device.</p>
            
            <p><strong>⏰ This link expires in 7 days.</strong></p>
            
            <p>If you have questions, reply to this email or call us at:<br>
            📞 {clinic_phone}</p>
            
            <p>Looking forward to meeting you!</p>
            
            <p>Warm regards,<br>
            <strong>The Celloxen Team</strong></p>
            
            <div class="disclaimer">
                <strong>⚠️ Disclaimer:</strong> This is a wellness assessment, not medical diagnosis or treatment. 
                Please consult a qualified healthcare provider for medical advice.
            </div>
        </div>
        <div class="footer">
            <p>Celloxen Health Portal<br>
            {clinic_address}<br>
            © 2025 Celloxen Health. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
    },
    
    "ACCOUNT_CONFIRMATION": {
        "subject": "Your Celloxen Account is Ready!",
        "template": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; }}
        .info-box {{ background: white; border: 2px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .score-box {{ background: #f0f4ff; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ background: #333; color: #fff; padding: 20px; text-align: center; font-size: 12px; border-radius: 0 0 10px 10px; }}
        .disclaimer {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome to Celloxen Health!</h1>
        </div>
        <div class="content">
            <p>Dear {patient_name},</p>
            
            <p>Your wellness profile has been successfully created!</p>
            
            <div class="info-box">
                <h3>ACCOUNT DETAILS</h3>
                <p><strong>Username:</strong> {email}<br>
                <strong>Portal:</strong> <a href="https://celloxen.com/patient-portal">celloxen.com/patient-portal</a></p>
            </div>
            
            <div class="info-box">
                <h3>YOUR WELLNESS SNAPSHOT</h3>
                <p><strong>Overall Wellness Score: {overall_score}/100</strong></p>
                <div class="score-box">
                    <strong>Domain Scores:</strong><br>
                    • Energy & Vitality: {energy_score}/100<br>
                    • Pain & Mobility: {pain_score}/100<br>
                    • Stress Management: {stress_score}/100<br>
                    • Metabolic Balance: {metabolic_score}/100<br>
                    • Sleep Quality: {sleep_score}/100
                </div>
            </div>
            
            <h3>WHAT'S NEXT:</h3>
            <ol>
                <li>We'll schedule your comprehensive assessment</li>
                <li>You'll receive an appointment confirmation</li>
                <li>At your visit, we'll conduct iris imaging</li>
                <li>You'll receive a detailed wellness report</li>
                <li>We'll create your personalized therapy plan</li>
            </ol>
            
            <p>You can login to your portal anytime to:</p>
            <ul>
                <li>✓ View your wellness information</li>
                <li>✓ Track your progress</li>
                <li>✓ Communicate with us</li>
                <li>✓ Manage appointments</li>
            </ul>
            
            <div style="text-align: center;">
                <a href="https://celloxen.com/patient-portal" class="button">Login to Your Portal</a>
            </div>
            
            <p>If you have any questions before your appointment, feel free to use the chat assistant in your portal or contact us directly.</p>
            
            <p>Looking forward to seeing you soon!</p>
            
            <p>The Celloxen Team<br>
            📞 {clinic_phone}<br>
            📧 health@celloxen.com</p>
            
            <div class="disclaimer">
                <strong>⚠️ Remember:</strong> This is a wellness assessment, not medical diagnosis or treatment.
            </div>
        </div>
        <div class="footer">
            <p>Celloxen Health Portal<br>
            © 2025 Celloxen Health. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
    },
    
    "APPOINTMENT_CONFIRMATION": {
        "subject": "Your Celloxen Appointment is Confirmed",
        "template": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; }}
        .appointment-box {{ background: white; border: 3px solid #28a745; padding: 25px; margin: 20px 0; border-radius: 10px; text-align: center; }}
        .info-section {{ background: #e8f4f8; padding: 20px; margin: 15px 0; border-radius: 5px; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 10px 5px; }}
        .footer {{ background: #333; color: #fff; padding: 20px; text-align: center; font-size: 12px; border-radius: 0 0 10px 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Appointment Confirmed</h1>
        </div>
        <div class="content">
            <p>Dear {patient_name},</p>
            
            <p>Your comprehensive wellness assessment is scheduled!</p>
            
            <div class="appointment-box">
                <h2>APPOINTMENT DETAILS</h2>
                <p style="font-size: 18px;">
                <strong>📅 Date:</strong> {appointment_date}<br>
                <strong>🕐 Time:</strong> {appointment_time}<br>
                <strong>⏱️ Duration:</strong> {duration} minutes<br>
                <strong>👤 Practitioner:</strong> {practitioner_name}<br>
                <strong>📍 Location:</strong> {clinic_name}
                </p>
            </div>
            
            <div class="info-section">
                <h3>ADDRESS:</h3>
                <p>{clinic_address}</p>
            </div>
            
            <div class="info-section">
                <h3>WHAT TO EXPECT:</h3>
                <p>During your visit, we'll:</p>
                <ul>
                    <li>✓ Review your wellness profile</li>
                    <li>✓ Conduct guided assessment via our chatbot</li>
                    <li>✓ Capture iris images for analysis</li>
                    <li>✓ Discuss initial findings</li>
                    <li>✓ Create your personalized therapy plan</li>
                </ul>
            </div>
            
            <div class="info-section">
                <h3>PLEASE PREPARE:</h3>
                <ul>
                    <li>• Arrive 10 minutes early</li>
                    <li>• Bring any relevant medical documents</li>
                    <li>• Wear comfortable clothing</li>
                    <li>• Remove contact lenses before iris imaging</li>
                    <li>• Avoid caffeine 2 hours before appointment</li>
                </ul>
            </div>
            
            <h3>NEED TO RESCHEDULE?</h3>
            <p>Login to your portal or call us:</p>
            
            <div style="text-align: center;">
                <a href="https://celloxen.com/patient-portal" class="button">Patient Portal</a>
                <a href="tel:{clinic_phone}" class="button" style="background: #28a745;">Call Us</a>
            </div>
            
            <p style="text-align: center; margin-top: 20px;">
            <strong>We look forward to seeing you!</strong>
            </p>
            
            <p>The Celloxen Team</p>
        </div>
        <div class="footer">
            <p>Celloxen Health Portal<br>
            📞 {clinic_phone} | 📧 health@celloxen.com<br>
            © 2025 Celloxen Health. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
    }
}


def get_db():
    """Get database connection"""
    return psycopg2.connect(
        host="localhost",
        database="celloxen_portal",
        user="celloxen_user",
        password="celloxen_secure_2024"
    )


def send_email(to_email: str, subject: str, html_content: str, email_type: str, patient_id: Optional[int] = None) -> bool:
    """
    Send email via IONOS SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        email_type: Type of email (for logging)
        patient_id: Patient ID (for logging)
    
    Returns:
        bool: True if sent successfully, False otherwise
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
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        # Log successful send
        log_email(patient_id, email_type, to_email, subject, 'SENT')
        
        return True
        
    except Exception as e:
        # Log failed send
        log_email(patient_id, email_type, to_email, subject, 'FAILED', str(e))
        print(f"Email send failed: {e}")
        return False


def log_email(patient_id: Optional[int], email_type: str, sent_to_email: str, subject: str, status: str, error_message: Optional[str] = None):
    """Log email to database"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO email_logs 
            (patient_id, email_type, sent_to_email, subject, status, sent_at, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (patient_id, email_type, sent_to_email, subject, status, datetime.now(), error_message))
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Email logging failed: {e}")


def send_invitation_email(patient_id: int, patient_name: str, email: str, registration_token: str, clinic_phone: str = "01224 123456", clinic_address: str = "Aberdeen Wellness Centre") -> bool:
    """Send invitation email to patient"""
    
    registration_link = f"https://celloxen.com/register/{registration_token}"
    
    html_content = EMAIL_TEMPLATES["INVITATION"]["template"].format(
        patient_name=patient_name,
        registration_link=registration_link,
        clinic_phone=clinic_phone,
        clinic_address=clinic_address
    )
    
    return send_email(
        to_email=email,
        subject=EMAIL_TEMPLATES["INVITATION"]["subject"],
        html_content=html_content,
        email_type="INVITATION",
        patient_id=patient_id
    )


def send_account_confirmation_email(patient_id: int, patient_name: str, email: str, wellness_scores: dict, clinic_phone: str = "01224 123456") -> bool:
    """Send account confirmation email"""
    
    html_content = EMAIL_TEMPLATES["ACCOUNT_CONFIRMATION"]["template"].format(
        patient_name=patient_name,
        email=email,
        overall_score=wellness_scores.get('overall', 0),
        energy_score=wellness_scores.get('energy_vitality', 0),
        pain_score=wellness_scores.get('pain_mobility', 0),
        stress_score=wellness_scores.get('stress_management', 0),
        metabolic_score=wellness_scores.get('metabolic_balance', 0),
        sleep_score=wellness_scores.get('sleep_quality', 0),
        clinic_phone=clinic_phone
    )
    
    return send_email(
        to_email=email,
        subject=EMAIL_TEMPLATES["ACCOUNT_CONFIRMATION"]["subject"],
        html_content=html_content,
        email_type="ACCOUNT_CONFIRMATION",
        patient_id=patient_id
    )


def send_appointment_confirmation_email(patient_id: int, patient_name: str, email: str, appointment_details: dict) -> bool:
    """Send appointment confirmation email"""
    
    html_content = EMAIL_TEMPLATES["APPOINTMENT_CONFIRMATION"]["template"].format(
        patient_name=patient_name,
        appointment_date=appointment_details.get('date', ''),
        appointment_time=appointment_details.get('time', ''),
        duration=appointment_details.get('duration', '60'),
        practitioner_name=appointment_details.get('practitioner', 'Our Practitioner'),
        clinic_name=appointment_details.get('clinic_name', 'Celloxen Wellness Centre'),
        clinic_address=appointment_details.get('clinic_address', ''),
        clinic_phone=appointment_details.get('clinic_phone', '01224 123456')
    )
    
    return send_email(
        to_email=email,
        subject=EMAIL_TEMPLATES["APPOINTMENT_CONFIRMATION"]["subject"],
        html_content=html_content,
        email_type="APPOINTMENT_CONFIRMATION",
        patient_id=patient_id
    )
