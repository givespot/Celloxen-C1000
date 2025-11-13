"""
Email Templates for Celloxen Health Portal
All email templates in one place
"""

from datetime import datetime


def get_invitation_email(patient_name: str, registration_link: str, clinic_phone: str = "01224 123456") -> dict:
    """Generate invitation email"""
    
    subject = "Welcome to Your Wellness Journey with Celloxen"
    
    html = f"""
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
            © 2025 Celloxen Health. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
    """
    
    return {"subject": subject, "html": html}


def get_account_confirmation_email(patient_name: str, email: str, overall_score: float) -> dict:
    """Generate account confirmation email"""
    
    subject = "Your Celloxen Account is Ready!"
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; }}
        .info-box {{ background: white; border: 2px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 5px; }}
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
                <p>We'll discuss your detailed results during your clinic visit.</p>
            </div>
            
            <h3>WHAT'S NEXT:</h3>
            <ol>
                <li>We'll schedule your comprehensive assessment</li>
                <li>You'll receive an appointment confirmation</li>
                <li>At your visit, we'll conduct iris imaging</li>
                <li>You'll receive a detailed wellness report</li>
                <li>We'll create your personalized therapy plan</li>
            </ol>
            
            <div style="text-align: center;">
                <a href="https://celloxen.com/patient-portal" class="button">Login to Your Portal</a>
            </div>
            
            <p>Looking forward to seeing you soon!</p>
            
            <p>The Celloxen Team</p>
            
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
    
    return {"subject": subject, "html": html}


def get_test_email() -> dict:
    """Generate test email"""
    
    subject = "Celloxen Email System Test"
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #f0f4ff; padding: 30px; border-radius: 10px; }}
        h2 {{ color: #667eea; }}
        .success {{ background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>✅ Email System Test</h2>
        <div class="success">
            <strong>Success!</strong> The Celloxen email system is working correctly.
        </div>
        <p><strong>Configuration:</strong></p>
        <ul>
            <li>Server: smtp.ionos.co.uk</li>
            <li>Port: 587</li>
            <li>Account: health@celloxen.com</li>
        </ul>
        <p style="color: #666; font-size: 12px;">Sent: {datetime.now()}</p>
    </div>
</body>
</html>
    """
    
    return {"subject": subject, "html": html}
