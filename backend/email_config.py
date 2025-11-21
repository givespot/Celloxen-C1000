"""
Email System Configuration for Super Admin - IONOS
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# IONOS SMTP Settings
SMTP_SERVER = "smtp.ionos.co.uk"
SMTP_PORT = 587
SMTP_USERNAME = "health@celloxen.com"
SMTP_PASSWORD = "Kuwait1000$$"
FROM_EMAIL = "health@celloxen.com"
FROM_NAME = "Celloxen Health Portal"

def send_email(to_email, subject, html_body, text_body=None):
    """
    Send an email using IONOS SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content of email
        text_body: Plain text version (optional)
    
    Returns:
        dict: {"success": bool, "message": str}
    """
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = to_email
        
        # Add text and HTML parts
        if text_body:
            part1 = MIMEText(text_body, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(html_body, 'html')
        msg.attach(part2)
        
        # Connect to IONOS SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        return {
            "success": True,
            "message": "Email sent successfully"
        }
        
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": "SMTP Authentication failed. Check username/password."
        }
    except smtplib.SMTPException as e:
        return {
            "success": False,
            "message": f"SMTP Error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error sending email: {str(e)}"
        }


def create_welcome_email_html(clinic_name, login_url, email, temp_password):
    """Create HTML email for welcome message"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
            }}
            .header {{
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 32px;
            }}
            .content {{
                padding: 40px 30px;
                background: #f9fafb;
            }}
            .credentials-box {{
                background: white;
                border: 3px solid #3b82f6;
                border-radius: 12px;
                padding: 25px;
                margin: 25px 0;
            }}
            .credentials-box h3 {{
                color: #1e3a8a;
                margin-top: 0;
                margin-bottom: 20px;
            }}
            .credential-item {{
                margin: 15px 0;
                padding: 12px;
                background: #f1f5f9;
                border-radius: 8px;
            }}
            .credential-label {{
                font-weight: 600;
                color: #1e3a8a;
                font-size: 14px;
                margin-bottom: 5px;
            }}
            .credential-value {{
                font-family: 'Courier New', monospace;
                font-size: 16px;
                color: #0f172a;
                font-weight: 600;
            }}
            .button {{
                display: inline-block;
                background: #1e3a8a;
                color: white !important;
                padding: 15px 40px;
                text-decoration: none;
                border-radius: 8px;
                margin: 20px 0;
                font-weight: 600;
                font-size: 16px;
            }}
            .warning {{
                background: #fef3c7;
                border-left: 5px solid #f59e0b;
                padding: 20px;
                margin: 25px 0;
                border-radius: 8px;
            }}
            .warning strong {{
                color: #92400e;
            }}
            .features {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .features ul {{
                list-style: none;
                padding: 0;
            }}
            .features li {{
                padding: 8px 0;
                padding-left: 30px;
                position: relative;
            }}
            .features li:before {{
                content: "✅";
                position: absolute;
                left: 0;
            }}
            .footer {{
                text-align: center;
                padding: 30px;
                background: #1e293b;
                color: white;
            }}
            .footer p {{
                margin: 5px 0;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 Welcome to Celloxen!</h1>
                <p style="margin-top: 10px; font-size: 18px;">Your Health Portal is Ready</p>
            </div>
            
            <div class="content">
                <h2 style="color: #1e3a8a;">Hello {clinic_name},</h2>
                
                <p>We're thrilled to have you join the Celloxen Health Portal platform! Your clinic account has been successfully created and is ready to use.</p>
                
                <div class="credentials-box">
                    <h3>🔐 Your Login Credentials</h3>
                    
                    <div class="credential-item">
                        <div class="credential-label">Portal URL</div>
                        <div class="credential-value">{login_url}</div>
                    </div>
                    
                    <div class="credential-item">
                        <div class="credential-label">Email Address</div>
                        <div class="credential-value">{email}</div>
                    </div>
                    
                    <div class="credential-item">
                        <div class="credential-label">Temporary Password</div>
                        <div class="credential-value">{temp_password}</div>
                    </div>
                </div>
                
                <div class="warning">
                    <strong>⚠️ IMPORTANT SECURITY NOTICE</strong>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>This is a temporary password</li>
                        <li>You will be required to change it on your first login</li>
                        <li>Please keep your credentials secure and confidential</li>
                        <li>Never share your password with anyone</li>
                    </ul>
                </div>
                
                <center>
                    <a href="{login_url}" class="button">Login to Your Portal Now</a>
                </center>
                
                <h3 style="color: #1e3a8a; margin-top: 30px;">🚀 Getting Started:</h3>
                <ol style="line-height: 1.8;">
                    <li>Click the button above or visit <strong>{login_url}</strong></li>
                    <li>Log in using your email and temporary password</li>
                    <li>Create a new secure password when prompted</li>
                    <li>Complete your clinic profile information</li>
                    <li>Start adding patients and managing appointments</li>
                </ol>
                
                <div class="features">
                    <h3 style="color: #1e3a8a; margin-top: 0;">✨ Features Available to You:</h3>
                    <ul>
                        <li>Patient Management System</li>
                        <li>Appointment Scheduling</li>
                        <li>AI-Powered Iridology Analysis</li>
                        <li>Digital Health Records</li>
                        <li>Staff Management</li>
                        <li>Secure GDPR-Compliant Data Storage</li>
                        <li>Professional Report Generation</li>
                    </ul>
                </div>
                
                <p style="margin-top: 30px;"><strong>Need Help?</strong><br>
                If you have any questions or need assistance getting started, please don't hesitate to contact our support team at <a href="mailto:health@celloxen.com" style="color: #3b82f6;">health@celloxen.com</a></p>
                
                <p style="margin-top: 20px;">Best regards,<br>
                <strong>The Celloxen Team</strong></p>
            </div>
            
            <div class="footer">
                <p><strong>CELLOXEN HEALTH PORTAL</strong></p>
                <p>This is an automated message. Please do not reply to this email.</p>
                <p style="margin-top: 10px;">&copy; 2025 Celloxen Health Portal. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

# Database Settings
DB_HOST = "localhost"
DB_NAME = "celloxen_portal"
DB_USER = "celloxen_user"
DB_PASSWORD = "CelloxenSecure2025"
