"""
Invitation API - Send registration invitations to patients
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import secrets
import string

from email_sender import send_email
from email_templates import get_invitation_email
from email_config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

router = APIRouter(prefix="/api/v1/invitations", tags=["invitations"])


def get_db():
    """Get database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


class InvitationRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None


@router.post("/send")
async def send_invitation(request: InvitationRequest):
    """
    Send registration invitation to a patient
    - If patient exists: Update with new token
    - If patient doesn't exist: Create new patient with token
    """
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if patient already exists
        cur.execute("SELECT id, email FROM patients WHERE email = %s", (request.email,))
        existing_patient = cur.fetchone()
        
        # Generate token
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(32))
        expires_at = datetime.now() + timedelta(days=7)
        
        if existing_patient:
            # Patient exists - just update token
            patient_id = existing_patient['id']
            
            cur.execute("""
                UPDATE patients
                SET registration_token = %s,
                    token_expires_at = %s,
                    status = 'INVITED'
                WHERE id = %s
            """, (token, expires_at, patient_id))
            
        else:
            # New patient - create record
            patient_number = f"P{datetime.now().strftime('%Y%m%d')}{secrets.randbelow(10000):04d}"
            clinic_id = 1  # Default clinic
            default_dob = datetime(1990, 1, 1).date()
            
            cur.execute("""
                INSERT INTO patients 
                (patient_number, clinic_id, first_name, last_name, email, mobile_phone, 
                 date_of_birth, registration_token, token_expires_at, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'INVITED')
                RETURNING id
            """, (patient_number, clinic_id, request.first_name, request.last_name, 
                  request.email, request.phone or '', default_dob, token, expires_at))
            
            result = cur.fetchone()
            patient_id = result['id']
        
        conn.commit()
        
        # Send invitation email
        template = get_invitation_email(
            patient_name=f"{request.first_name} {request.last_name}",
            registration_link=f"https://celloxen.com/patient-register.html?token={token}"
        )
        
        success, message = send_email(
            to_email=request.email,
            subject=template['subject'],
            html_content=template['html'],
            patient_id=patient_id,
            email_type="INVITATION"
        )
        
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Invitation sent successfully",
            "patient_id": patient_id,
            "email": request.email,
            "token": token,
            "expires_in_days": 7
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
