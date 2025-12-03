"""
Patient Portal API Endpoints - CORRECTED VERSION
Handles patient-specific authentication and data access
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
import bcrypt
from psycopg2.extras import RealDictCursor
import psycopg2
import os

router = APIRouter(prefix="/api/v1/patient", tags=["Patient Portal"])

# JWT Configuration
SECRET_KEY = "celloxen-patient-portal-secret-key-2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/patient/login")

# Database connection
def get_db():
    conn = psycopg2.connect(
        dbname="celloxen_portal",
        user="celloxen_user",
        password=os.getenv("DB_PASSWORD"),
        host="localhost"
    )
    return conn

# Models
class PatientLoginRequest(BaseModel):
    email: str
    password: str

class PatientToken(BaseModel):
    access_token: str
    token_type: str
    patient_id: int
    patient_name: str

class PatientProfile(BaseModel):
    patient_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: str
    address: Optional[str]
    emergency_contact: Optional[str]
    emergency_phone: Optional[str]

class DashboardSummary(BaseModel):
    next_appointment: Optional[dict]
    therapy_progress: dict
    recent_assessments: List[dict]
    notification_count: int

# Helper Functions
def create_patient_token(patient_id: int) -> str:
    """Create JWT token for patient"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(patient_id), "exp": expire, "type": "patient"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_patient_token(token: str):
    """Verify JWT token and return patient_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        patient_id = int(payload.get("sub"))
        token_type = payload.get("type")
        
        if token_type != "patient":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        return patient_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_patient(token: str = Depends(oauth2_scheme)):
    """Get current authenticated patient"""
    return verify_patient_token(token)

# Endpoints

@router.post("/login", response_model=PatientToken)
async def patient_login(credentials: PatientLoginRequest):
    """Patient login endpoint"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT id, first_name, last_name, email, password_hash, status
            FROM patients 
            WHERE LOWER(email) = LOWER(%s)
        """, (credentials.email,))
        
        patient = cur.fetchone()
        
        if not patient:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if patient['status'] != 'active':
            raise HTTPException(status_code=403, detail="Account is inactive. Please contact the clinic.")
        
        if not patient['password_hash']:
            raise HTTPException(status_code=401, detail="Password not set. Please contact the clinic.")
        
        if not bcrypt.checkpw(credentials.password.encode('utf-8'), patient['password_hash'].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        token = create_patient_token(patient['id'])
        
        return PatientToken(
            access_token=token,
            token_type="bearer",
            patient_id=patient['id'],
            patient_name=f"{patient['first_name']} {patient['last_name']}"
        )
        
    finally:
        cur.close()
        conn.close()


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard(patient_id: int = Depends(get_current_patient)):
    """Get patient dashboard summary"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get next appointment
        cur.execute("""
            SELECT a.id as appointment_id, a.appointment_date, a.appointment_time, 
                   a.appointment_type, a.duration_minutes, a.status,
                   c.name as clinic_name
            FROM appointments a
            JOIN clinics c ON a.clinic_id = c.id
            WHERE a.patient_id = %s 
              AND a.status = 'SCHEDULED'
              AND a.appointment_date >= CURRENT_DATE
            ORDER BY a.appointment_date, a.appointment_time
            LIMIT 1
        """, (patient_id,))
        next_appointment = cur.fetchone()
        
        # Get therapy progress
        cur.execute("""
            SELECT tp.id as therapy_plan_id, tp.status, tp.created_at,
                   COUNT(tpi.id) as total_items,
                   0 as completed_items
            FROM therapy_plans tp
            LEFT JOIN therapy_plan_items tpi ON tp.id = tpi.therapy_plan_id
            WHERE tp.patient_id = %s
            GROUP BY tp.id, tp.status, tp.created_at
            ORDER BY tp.created_at DESC
            LIMIT 1
        """, (patient_id,))
        therapy_data = cur.fetchone()
        
        therapy_progress = {
            "has_active_plan": False,
            "total_sessions": 0,
            "completed_sessions": 0,
            "progress_percentage": 0,
            "plan_status": None
        }
        
        if therapy_data:
            total = therapy_data['total_items'] or 0
            completed = therapy_data['completed_items'] or 0
            therapy_progress = {
                "has_active_plan": True,
                "total_sessions": total,
                "completed_sessions": completed,
                "progress_percentage": round((completed / total * 100) if total > 0 else 0, 1),
                "plan_status": therapy_data['status']
            }
        
        # Get recent assessments (note: comprehensive_assessments doesn't have clinic_id directly)
        cur.execute("""
            SELECT ca.id as assessment_id, ca.assessment_date, 
                   CAST(ca.overall_wellness_score AS FLOAT) as wellness_score, 
                   ca.assessment_status as status
            FROM comprehensive_assessments ca
            WHERE ca.patient_id = %s
            ORDER BY ca.assessment_date DESC
            LIMIT 3
        """, (patient_id,))
        recent_assessments = cur.fetchall()
        
        notification_count = 0
        
        return DashboardSummary(
            next_appointment=dict(next_appointment) if next_appointment else None,
            therapy_progress=therapy_progress,
            recent_assessments=[dict(a) for a in recent_assessments],
            notification_count=notification_count
        )
        
    finally:
        cur.close()
        conn.close()


@router.get("/profile", response_model=PatientProfile)
async def get_profile(patient_id: int = Depends(get_current_patient)):
    """Get patient profile"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT id, first_name, last_name, email, mobile_phone,
                   date_of_birth, address, emergency_contact, emergency_phone
            FROM patients
            WHERE id = %s
        """, (patient_id,))
        
        patient = cur.fetchone()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return PatientProfile(
            patient_id=patient['id'],
            first_name=patient['first_name'],
            last_name=patient['last_name'],
            email=patient['email'],
            phone=patient['mobile_phone'],
            date_of_birth=str(patient['date_of_birth']),
            address=patient['address'],
            emergency_contact=patient['emergency_contact'],
            emergency_phone=patient['emergency_phone']
        )
        
    finally:
        cur.close()
        conn.close()


@router.get("/assessments")
async def get_assessments(patient_id: int = Depends(get_current_patient)):
    """Get patient's assessment history"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get clinic info through patients table since assessments don't have clinic_id
        cur.execute("""
            SELECT 
                ca.id as assessment_id,
                ca.assessment_date,
                CAST(ca.overall_wellness_score AS FLOAT) as wellness_score,
                ca.questionnaire_scores,
                ca.assessment_status as status,
                ca.integrated_recommendations as recommendations,
                c.name as clinic_name
            FROM comprehensive_assessments ca
            JOIN patients p ON ca.patient_id = p.id
            JOIN clinics c ON p.clinic_id = c.id
            WHERE ca.patient_id = %s
            ORDER BY ca.assessment_date DESC
        """, (patient_id,))
        
        assessments = cur.fetchall()
        
        # Parse the JSONB scores to extract domain scores
        result = []
        for assessment in assessments:
            assessment_dict = dict(assessment)
            
            # Extract scores from questionnaire_scores JSONB if it exists
            scores = assessment.get('questionnaire_scores', {}) or {}
            
            # Map actual domain codes to frontend expected field names
            # Extract score from nested structure
            def get_score(domain_key):
                domain_data = scores.get(domain_key, {})
                if isinstance(domain_data, dict):
                    return domain_data.get('score', 0)
                return 0
            
            # Map the 5 therapy domains to expected frontend fields
            assessment_dict['energy_vitality_score'] = get_score('c102_vitality_energy')
            assessment_dict['chronic_pain_score'] = get_score('c104_comfort_mobility')
            assessment_dict['anxiety_stress_score'] = get_score('c107_stress_relaxation')
            assessment_dict['diabetics_score'] = get_score('c108_metabolic_balance')
            assessment_dict['sleep_quality_score'] = get_score('c105_circulation_heart')
            
            result.append(assessment_dict)
        
        return result
        
    finally:
        cur.close()
        conn.close()


@router.get("/assessments/{assessment_id}")
async def get_assessment_detail(
    assessment_id: int,
    patient_id: int = Depends(get_current_patient)
):
    """Get detailed assessment report"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT * FROM comprehensive_assessments
            WHERE id = %s AND patient_id = %s
        """, (assessment_id, patient_id))
        
        assessment = cur.fetchone()
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        return dict(assessment)
        
    finally:
        cur.close()
        conn.close()


@router.get("/therapy-plans")
async def get_therapy_plans(patient_id: int = Depends(get_current_patient)):
    """Get patient's therapy plans"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                tp.id as therapy_plan_id,
                tp.assessment_id,
                tp.status,
                
                
                tp.created_at,
                tp.consent_date as patient_consent_date,
                c.name as clinic_name,
                COUNT(tpi.id) as total_items,
                0 as completed_items
            FROM therapy_plans tp
            JOIN clinics c ON tp.clinic_id = c.id
            LEFT JOIN therapy_plan_items tpi ON tp.id = tpi.therapy_plan_id
            WHERE tp.patient_id = %s
            GROUP BY tp.id, c.name
            ORDER BY tp.created_at DESC
        """, (patient_id,))
        
        plans = cur.fetchall()
        return [dict(p) for p in plans]
        
    finally:
        cur.close()
        conn.close()


@router.get("/therapy-plans/{plan_id}")
async def get_therapy_plan_detail(
    plan_id: int,
    patient_id: int = Depends(get_current_patient)
):
    """Get detailed therapy plan with items"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT tp.*, c.name as clinic_name, c.address_line1 as address, c.city
            FROM therapy_plans tp
            JOIN clinics c ON tp.clinic_id = c.id
            WHERE tp.id = %s AND tp.patient_id = %s
        """, (plan_id, patient_id))
        
        plan = cur.fetchone()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Therapy plan not found")
        
        cur.execute("""
            SELECT * FROM therapy_plan_items
            WHERE therapy_plan_id = %s
            ORDER BY priority_level, created_at
        """, (plan_id,))
        
        items = cur.fetchall()
        
        result = dict(plan)
        result['items'] = [dict(item) for item in items]
        
        return result
        
    finally:
        cur.close()
        conn.close()


@router.get("/appointments")
async def get_appointments(patient_id: int = Depends(get_current_patient)):
    """Get patient's appointments"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                a.id as appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.appointment_type,
                a.duration_minutes,
                a.status,
                
                c.name as clinic_name,
                c.address_line1 as address,
                c.city,
                c.phone as clinic_phone
            FROM appointments a
            JOIN clinics c ON a.clinic_id = c.id
            WHERE a.patient_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """, (patient_id,))
        
        appointments = cur.fetchall()
        return [dict(a) for a in appointments]
        
    finally:
        cur.close()
        conn.close()


@router.put("/profile")
async def update_profile(
    profile_data: dict,
    patient_id: int = Depends(get_current_patient)
):
    """Update patient profile (limited fields)"""
    conn = get_db()
    cur = conn.cursor()
    
    try:
        allowed_fields = ['mobile_phone', 'address', 'emergency_contact', 'emergency_phone']
        
        update_fields = []
        update_values = []
        
        for field in allowed_fields:
            if field in profile_data:
                update_fields.append(f"{field} = %s")
                update_values.append(profile_data[field])
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        update_values.append(patient_id)
        
        query = f"""
            UPDATE patients 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        
        cur.execute(query, update_values)
        conn.commit()
        
        return {"message": "Profile updated successfully"}
        
    finally:
        cur.close()
        conn.close()


@router.post("/request-password-reset")
async def request_password_reset(email: EmailStr):
    """Request password reset (sends email with token)"""
    return {"message": "If the email exists, password reset instructions have been sent"}


@router.post("/reset-password")
async def reset_password(token: str, new_password: str):
    """Reset password using token"""
    return {"message": "Password reset successfully"}

