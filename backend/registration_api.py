"""
Registration API - Public endpoints for patient registration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from datetime import datetime
import json

from email_database import validate_token
from email_sender import send_email
from email_templates import get_account_confirmation_email
from email_config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

router = APIRouter(prefix="/api/v1/register", tags=["registration"])


def get_db():
    """Get database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


class RegistrationData(BaseModel):
    token: str
    password: str
    date_of_birth: str
    mobile_phone: str
    chatbot_answers: Dict[str, int]


@router.get("/questions")
async def get_registration_questions():
    """Get all wellness questions for chatbot"""
    try:
        questions = get_all_questions()
        return {
            "success": True,
            "total_questions": sum(len(q) for q in questions.values()),
            "domains": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate/{token}")
async def validate_registration_token(token: str):
    """Validate registration token"""
    try:
        patient_data = validate_token(token)
        
        if not patient_data:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        return {
            "valid": True,
            "patient_id": patient_data['id'],
            "first_name": patient_data['first_name'],
            "last_name": patient_data['last_name'],
            "email": patient_data['email']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete")
async def complete_registration(data: RegistrationData):
    """Complete patient registration"""
    try:
        # Validate token
        patient_data = validate_token(data.token)
        if not patient_data:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        patient_id = patient_data['id']
        
        # Calculate wellness scores
        scores = calculate_all_scores(data.chatbot_answers)
        
        # Hash password
        password_hash = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update patient record
        conn = get_db()
        cur = conn.cursor()
        
        # Update patient with password, DOB, phone, and status
        cur.execute("""
            UPDATE patients
            SET password_hash = %s,
                date_of_birth = %s,
                mobile_phone = %s,
                status = 'active',
                portal_access = TRUE,
                registration_token = NULL,
                token_expires_at = NULL
            WHERE id = %s
        """, (password_hash, data.date_of_birth, data.mobile_phone, patient_id))
        
        # Save wellness questionnaire to comprehensive_assessments
        # Match the actual table structure
        questionnaire_scores = {
            'overall_score': scores['overall_score'],
            'energy_vitality': scores['energy_vitality'],
            'pain_mobility': scores['pain_mobility'],
            'stress_management': scores['stress_management'],
            'metabolic_balance': scores['metabolic_balance'],
            'sleep_quality': scores['sleep_quality']
        }
        
        cur.execute("""
            INSERT INTO comprehensive_assessments 
            (patient_id, assessment_date, assessment_status, 
             questionnaire_responses, questionnaire_scores, overall_wellness_score)
            VALUES (%s, %s, 'completed', %s, %s, %s)
        """, (
            patient_id,
            datetime.now(),
            json.dumps(data.chatbot_answers),
            json.dumps(questionnaire_scores),
            scores['overall_score']
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Send confirmation email
        template = get_account_confirmation_email(
            patient_name=f"{patient_data['first_name']} {patient_data['last_name']}",
            email=patient_data['email'],
            overall_score=scores['overall_score']
        )
        
        send_email(
            to_email=patient_data['email'],
            subject=template['subject'],
            html_content=template['html'],
            patient_id=patient_id,
            email_type="ACCOUNT_CONFIRMATION"
        )
        
        return {
            "success": True,
            "message": "Registration completed successfully",
            "patient_id": patient_id,
            "wellness_scores": scores,
            "email_sent": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
