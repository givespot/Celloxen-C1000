import bcrypt
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from models import AppointmentCreate, PatientCreate, PatientUpdate, AssessmentCreate, AssessmentUpdate, TherapyPlanCreate, TherapyPlanUpdate
from enhanced_chatbot import router as chatbot_router
from patient_portal_endpoints import router as patient_router
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from datetime import datetime
import json
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from ai_iridology_analyzer import AIIridologyAnalyzer
from new_assessment_module import router as new_assessment_router
from enhanced_dashboard_api import router as dashboard_router
from fastapi.responses import StreamingResponse

# Assessment Module Imports
from celloxen_assessment_system import (
    ASSESSMENT_QUESTIONS,
    THERAPY_PROTOCOLS,
    calculate_assessment_score,
    generate_therapy_recommendations,
    generate_multi_domain_recommendations
)

# Initialize AI analyzer and report generator
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "celloxen_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "celloxen_portal")

ai_analyzer = AIIridologyAnalyzer(ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# Database connection context manager
@asynccontextmanager
async def get_db_connection():
    """Context manager for database connections"""
    conn = await asyncpg.connect(
        host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )
    try:
        yield conn
    finally:
        await conn.close()


# Database connection context manager

def convert_date_string(date_str):
    """Convert date string to date object"""
    from datetime import date
    if date_str is None or isinstance(date_str, date):
        return date_str
    if isinstance(date_str, str):
        try:
            if '-' in date_str:
                year, month, day = date_str.split('-')
            elif '/' in date_str:
                day, month, year = date_str.split('/')
            else:
                return None
            return date(int(year), int(month), int(day))
        except:
            return None
    return None

app = FastAPI()

# Include patient portal router
app.include_router(patient_router)
app.include_router(dashboard_router)
app.include_router(new_assessment_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://celloxen.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI analyzer and report generator
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "celloxen_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "celloxen_portal")

ai_analyzer = AIIridologyAnalyzer(ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# Database connection context manager

# Token verification helper function

# JWT Configuration
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "celloxen_secret_key_2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify JWT token and return user info"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        clinic_id = payload.get("clinic_id")
        
        if user_id is None:
            return None
            
        return {
            "user_id": int(user_id),
            "clinic_id": int(clinic_id) if clinic_id else None
        }
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return None

@app.post("/api/v1/auth/login")
async def login(user_credentials: dict):
    try:
        email = user_credentials.get("email")
        password = user_credentials.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
        if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            await conn.close()
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        await conn.close()
        
        return {
            "access_token": create_access_token({
                "sub": str(user['id']),
                "clinic_id": user['clinic_id'],
                "email": user['email']
            }),
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user['full_name'],
                "role": user['role'],
                "status": user['status'],
                "clinic_id": user['clinic_id']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/auth/me")
async def get_current_user():
    return {"id": 1, "email": "admin@celloxen.com", "role": "super_admin"}


# Password Reset Endpoints - Added 30/11/2025
import secrets

@app.post("/api/v1/auth/forgot-password")
async def forgot_password(request_data: dict):
    """Request password reset - sends reset token"""
    try:
        email = request_data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )

        # Check if user exists
        user = await conn.fetchrow("SELECT id, email, full_name FROM users WHERE email = $1", email)

        if not user:
            await conn.close()
            # Return success even if user not found (security best practice)
            return {"success": True, "message": "If the email exists, a reset link has been sent"}

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # Store reset token in database (create table if needed via try/except)
        try:
            await conn.execute("""
                INSERT INTO password_reset_tokens (user_id, token, expires_at, created_at)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (user_id) DO UPDATE SET token = $2, expires_at = $3, created_at = NOW()
            """, user['id'], reset_token, expires_at)
        except Exception as e:
            # Table might not exist, create it
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE REFERENCES users(id),
                    token VARCHAR(255) NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            await conn.execute("""
                INSERT INTO password_reset_tokens (user_id, token, expires_at, created_at)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (user_id) DO UPDATE SET token = $2, expires_at = $3, created_at = NOW()
            """, user['id'], reset_token, expires_at)

        await conn.close()

        # In production, send email here. For now, return token in response for testing
        print(f"Password reset token for {email}: {reset_token}")

        return {
            "success": True,
            "message": "If the email exists, a reset link has been sent",
            # Remove token from response in production
            "debug_token": reset_token
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR in forgot-password: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/auth/verify-reset-token/{token}")
async def verify_reset_token(token: str):
    """Verify password reset token is valid"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )

        reset_request = await conn.fetchrow("""
            SELECT prt.*, u.email, u.full_name
            FROM password_reset_tokens prt
            JOIN users u ON prt.user_id = u.id
            WHERE prt.token = $1 AND prt.expires_at > NOW()
        """, token)

        await conn.close()

        if not reset_request:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")

        return {
            "valid": True,
            "email": reset_request['email']
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR in verify-reset-token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/auth/reset-password")
async def reset_password(request_data: dict):
    """Reset password using token"""
    try:
        token = request_data.get("token")
        new_password = request_data.get("password")

        if not token or not new_password:
            raise HTTPException(status_code=400, detail="Token and new password are required")

        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )

        # Verify token
        reset_request = await conn.fetchrow("""
            SELECT user_id FROM password_reset_tokens
            WHERE token = $1 AND expires_at > NOW()
        """, token)

        if not reset_request:
            await conn.close()
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")

        # Hash new password
        password_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Update password
        await conn.execute(
            "UPDATE users SET password_hash = $1 WHERE id = $2",
            password_hash, reset_request['user_id']
        )

        # Delete used token
        await conn.execute(
            "DELETE FROM password_reset_tokens WHERE user_id = $1",
            reset_request['user_id']
        )

        await conn.close()

        return {
            "success": True,
            "message": "Password reset successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR in reset-password: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/patients/stats/overview")
async def get_patient_stats():
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        total_patients = await conn.fetchval("SELECT COUNT(*) FROM patients")
        new_this_month = await conn.fetchval(
            """
            SELECT COUNT(*) FROM patients 
            WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
            """
        )
        assessments_completed = await conn.fetchval(
            """
            SELECT COUNT(*) FROM patient_assessments
            WHERE status = 'completed'
            AND DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
            """
        )
        await conn.close()
        return {
            "total_patients": total_patients,
            "active_patients": total_patients,
            "new_this_month": new_this_month,
            "assessments_completed": assessments_completed
        }
    except Exception as e:
        print(f"Error in patient stats: {str(e)}")
        return {"total_patients": 0, "active_patients": 0, "new_this_month": 0, "assessments_completed": 0}


@app.get("/api/v1/clinic/patients")
async def get_clinic_patients():
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        patients = await conn.fetch("""
            SELECT p.*, c.name as clinic_name 
            FROM patients p 
            LEFT JOIN clinics c ON p.clinic_id = c.id
            ORDER BY p.created_at DESC
        """)
        await conn.close()
        return [dict(patient) for patient in patients]
    except Exception as e:
        return []


@app.get("/api/v1/clinic/patients/{patient_id}")
async def get_patient(patient_id: int):
    """Get a single patient with all details"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get patient data
        patient = await conn.fetchrow("""
            SELECT p.*, c.name as clinic_name 
            FROM patients p 
            LEFT JOIN clinics c ON p.clinic_id = c.id
            WHERE p.id = $1
        """, patient_id)
        
        if not patient:
            await conn.close()
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get assessment count
        assessment_count = await conn.fetchval(
            "SELECT COUNT(*) FROM assessments WHERE patient_id = $1", patient_id
        )
        
        # Get appointment count
        appointment_count = await conn.fetchval(
            "SELECT COUNT(*) FROM appointments WHERE patient_id = $1", patient_id
        )
        
        # Get therapy plan count
        therapy_count = await conn.fetchval(
            "SELECT COUNT(*) FROM therapy_plans WHERE patient_id = $1", patient_id
        )
        
        # Get latest assessment
        latest_assessment = await conn.fetchrow("""
            SELECT assessment_number, overall_wellness_score, created_at
            FROM assessments 
            WHERE patient_id = $1 
            ORDER BY created_at DESC 
            LIMIT 1
        """, patient_id)
        
        # Get upcoming appointment
        upcoming_appointment = await conn.fetchrow("""
            SELECT appointment_number, appointment_date, appointment_time, status
            FROM appointments 
            WHERE patient_id = $1 AND appointment_date >= CURRENT_DATE
            ORDER BY appointment_date, appointment_time 
            LIMIT 1
        """, patient_id)
        
        await conn.close()
        
        return {
            "patient": dict(patient),
            "stats": {
                "assessment_count": assessment_count,
                "appointment_count": appointment_count,
                "therapy_count": therapy_count
            },
            "latest_assessment": dict(latest_assessment) if latest_assessment else None,
            "upcoming_appointment": dict(upcoming_appointment) if upcoming_appointment else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR getting patient: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/clinic/patients/{patient_id}")
async def update_patient(patient_id: int, patient_data: dict):
    """Update a patient's information"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Parse date of birth if provided
        dob = None
        if patient_data.get('date_of_birth'):
            from datetime import datetime
            dob = datetime.strptime(patient_data.get('date_of_birth'), "%Y-%m-%d").date()
        
        # Update patient
        await conn.execute("""
            UPDATE patients SET
                first_name = COALESCE($1, first_name),
                last_name = COALESCE($2, last_name),
                email = COALESCE($3, email),
                mobile_phone = COALESCE($4, mobile_phone),
                date_of_birth = COALESCE($5, date_of_birth),
                gender = COALESCE($6, gender),
                address_line1 = COALESCE($7, address_line1),
                address_line2 = COALESCE($8, address_line2),
                city = COALESCE($9, city),
                county = COALESCE($10, county),
                postcode = COALESCE($11, postcode),
                emergency_contact = COALESCE($12, emergency_contact),
                emergency_phone = COALESCE($13, emergency_phone),
                emergency_relationship = COALESCE($14, emergency_relationship),
                medical_conditions = COALESCE($15, medical_conditions),
                medications = COALESCE($16, medications),
                allergies = COALESCE($17, allergies),
                insurance_details = COALESCE($18, insurance_details),
                notes = COALESCE($19, notes),
                status = COALESCE($20, status)
            WHERE id = $21
        """,
            patient_data.get('first_name'),
            patient_data.get('last_name'),
            patient_data.get('email'),
            patient_data.get('mobile_phone'),
            dob,
            patient_data.get('gender'),
            patient_data.get('address_line1'),
            patient_data.get('address_line2'),
            patient_data.get('city'),
            patient_data.get('county'),
            patient_data.get('postcode'),
            patient_data.get('emergency_contact'),
            patient_data.get('emergency_phone'),
            patient_data.get('emergency_relationship'),
            patient_data.get('medical_conditions'),
            patient_data.get('medications'),
            patient_data.get('allergies'),
            patient_data.get('insurance_details'),
            patient_data.get('notes'),
            patient_data.get('status'),
            patient_id
        )
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Patient updated successfully",
            "patient_id": patient_id
        }
        
    except Exception as e:
        print(f"❌ ERROR updating patient: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/clinic/patients/{patient_id}")
async def delete_patient(patient_id: int):
    """Delete a patient (soft delete by setting status to deleted)"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Check if patient exists
        patient = await conn.fetchrow("SELECT * FROM patients WHERE id = $1", patient_id)
        if not patient:
            await conn.close()
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Soft delete - set status to 'deleted'
        await conn.execute(
            "UPDATE patients SET status = 'deleted' WHERE id = $1",
            patient_id
        )
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Patient deleted successfully",
            "patient_id": patient_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR deleting patient: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/clinic/patients/{patient_id}/assessments")
async def get_patient_assessments_by_id(patient_id: int):
    """Get all assessments for a specific patient"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )

        # Get comprehensive assessments for this patient
        assessments = await conn.fetch("""
            SELECT id, overall_wellness_score, assessment_status,
                   constitutional_type, constitutional_strength,
                   assessment_date, created_at, updated_at
            FROM comprehensive_assessments
            WHERE patient_id = $1
            ORDER BY created_at DESC
        """, patient_id)

        await conn.close()

        return {
            "success": True,
            "patient_id": patient_id,
            "total": len(assessments),
            "assessments": [dict(a) for a in assessments]
        }

    except Exception as e:
        print(f"❌ ERROR getting patient assessments: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/clinic/patients/{patient_id}/iridology")
async def get_patient_iridology(patient_id: int):
    """Get all iridology analyses for a specific patient"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )

        # Get iridology analyses for this patient
        analyses = await conn.fetch("""
            SELECT id, analysis_number, status, constitutional_type,
                   constitutional_strength, left_eye_image, right_eye_image,
                   created_at, updated_at, processing_completed_at
            FROM iridology_analyses
            WHERE patient_id = $1
            ORDER BY created_at DESC
        """, patient_id)

        await conn.close()

        return {
            "success": True,
            "patient_id": patient_id,
            "total": len(analyses),
            "analyses": [dict(a) for a in analyses]
        }

    except Exception as e:
        print(f"❌ ERROR getting patient iridology: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/clinic/patients")
async def create_patient(patient_data: dict):
    """Create a new patient with UK address fields"""
    print("🔍 DEBUG: Received patient_data:", patient_data)
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get clinic_id (default to 1 if not provided)
        clinic_id = patient_data.get('clinic_id', 1)
        
        # Generate patient number
        count = await conn.fetchval("SELECT COUNT(*) FROM patients WHERE clinic_id = $1", clinic_id)
        patient_number = f"CLX-ABD-{str(count + 1).zfill(5)}"
        
        # Parse date of birth (already in YYYY-MM-DD format from frontend)
        from datetime import datetime
        dob = datetime.strptime(patient_data.get('date_of_birth'), "%Y-%m-%d").date()
        
        # Insert patient with all new UK address fields
        patient_id = await conn.fetchval(
            """INSERT INTO patients (
                patient_number, clinic_id, first_name, last_name, email, mobile_phone,
                date_of_birth, gender, address_line1, address_line2, city, county, postcode,
                emergency_contact, emergency_phone, emergency_relationship,
                medical_conditions, medications, allergies, insurance_details, notes,
                status, portal_access, created_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16,
                $17, $18, $19, $20, $21, 'active', false, NOW()
            ) RETURNING id""",
            patient_number, 
            clinic_id,
            patient_data.get('first_name'),
            patient_data.get('last_name'),
            patient_data.get('email'),
            patient_data.get('mobile_phone'),
            dob,
            patient_data.get('gender', ''),
            patient_data.get('address_line1', ''),
            patient_data.get('address_line2', ''),
            patient_data.get('city', ''),
            patient_data.get('county', ''),
            patient_data.get('postcode', ''),
            patient_data.get('emergency_contact', ''),
            patient_data.get('emergency_phone', ''),
            patient_data.get('emergency_relationship', ''),
            patient_data.get('medical_conditions', ''),
            patient_data.get('medications', ''),
            patient_data.get('allergies', ''),
            patient_data.get('insurance_details', ''),
            patient_data.get('notes', '')
        )
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Patient created successfully",
            "patient_id": patient_id,
            "patient_number": patient_number
        }
        
    except Exception as e:
        print(f"❌ ERROR creating patient: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/clinic/patients/{patient_id}")
async def update_patient(patient_id: int, patient_data: dict):
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Convert date if provided
        birth_date = None
        if 'date_of_birth' in patient_data and patient_data['date_of_birth']:
            birth_date = datetime.strptime(patient_data['date_of_birth'], '%Y-%m-%d').date()
        
        await conn.execute("""
            UPDATE patients 
            SET first_name = $1, last_name = $2, email = $3, 
                mobile_phone = $4, date_of_birth = $5, address = $6,
                emergency_contact = $7, emergency_phone = $8,
                medical_conditions = $9, medications = $10, allergies = $11,
                insurance_details = $12, notes = $13
            WHERE id = $14
        """, 
        patient_data.get('first_name'), patient_data.get('last_name'),
        patient_data.get('email'), patient_data.get('mobile_phone'),
        birth_date, patient_data.get('address'),
        patient_data.get('emergency_contact'), patient_data.get('emergency_phone'),
        patient_data.get('medical_conditions'), patient_data.get('medications'),
        patient_data.get('allergies'), patient_data.get('insurance_details'),
        patient_data.get('notes'), patient_id
        )
        
        await conn.close()
        return {"success": True}
        
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/clinic/patients/{patient_id}")
async def delete_patient(patient_id: int):
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        await conn.execute("DELETE FROM patients WHERE id = $1", patient_id)
        await conn.close()
        return {"success": True}
        
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/clinic/patients/{patient_id}")

# ============================================================================
# CLINIC SUBSCRIPTION INVOICES
# ============================================================================

@app.get("/api/v1/clinic/invoices")
async def get_clinic_invoices(authorization: str = Header(None)):
    """Get all subscription invoices for logged-in clinic"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        invoices = await conn.fetch("""
            SELECT id, invoice_number, amount, description,
                   due_date, payment_status as status, created_at
            FROM clinic_invoices
            WHERE clinic_id = $1
            ORDER BY created_at DESC
        """, user['clinic_id'])
        
        await conn.close()
        
        return {"success": True, "invoices": [dict(inv) for inv in invoices]}
    except Exception as e:
        print(f"Error fetching invoices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch invoices")

@app.get("/api/v1/clinic/invoices/{invoice_id}")
async def get_clinic_invoice(invoice_id: int, authorization: str = Header(None)):
    """Get single invoice detail for logged-in clinic"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        invoice = await conn.fetchrow("""
            SELECT ci.*, c.clinic_name, c.address_line1, c.city, 
                   c.postcode, c.email, c.phone
            FROM clinic_invoices ci
            JOIN clinics c ON ci.clinic_id = c.id
            WHERE ci.id = $1 AND ci.clinic_id = $2
        """, invoice_id, user['clinic_id'])
        
        await conn.close()
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        inv = dict(invoice)
        return {
            "success": True,
            "invoice": {
                "id": inv['id'],
                "invoice_number": inv['invoice_number'],
                "amount": float(inv['amount']),
                "description": inv['description'],
                "due_date": str(inv['due_date']),
                "payment_status": inv['payment_status'],
                "issue_date": str(inv['created_at'].date()) if inv.get('created_at') else None,
                "clinic": {
                    "name": inv['clinic_name'],
                    "address_line1": inv['address_line1'],
                    "city": inv['city'],
                    "postcode": inv['postcode'],
                    "email": inv['email'],
                    "phone": inv.get('phone')
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {str(e)}")

@app.put("/api/v1/clinic/invoices/{invoice_id}/mark-paid")
async def mark_invoice_paid(invoice_id: int, authorization: str = Header(None)):
    """Mark invoice as paid - Clinic staff only"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Verify invoice belongs to user's clinic
        invoice = await conn.fetchrow("""
            SELECT id, payment_status FROM clinic_invoices
            WHERE id = $1 AND clinic_id = $2
        """, invoice_id, user['clinic_id'])
        
        if not invoice:
            await conn.close()
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Update invoice to paid
        from datetime import datetime
        await conn.execute("""
            UPDATE clinic_invoices
            SET payment_status = 'paid',
                payment_date = $1,
                updated_at = $2
            WHERE id = $3
        """, datetime.now().date(), datetime.now(), invoice_id)
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Invoice marked as paid"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error marking invoice paid: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update invoice")

# ============================================
# PATIENT INVOICES ENDPOINTS
# ============================================

@app.get("/api/v1/patient-invoices")
async def get_patient_invoices(
    patient_id: int = None, 
    status: str = None,
    authorization: str = Header(None)
):
    """Get all patient invoices for clinic, optionally filtered by patient_id or status"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Build query based on filters
        query = """
            SELECT pi.*, p.first_name, p.last_name, p.email
            FROM patient_invoices pi
            JOIN patients p ON pi.patient_id = p.id
            WHERE pi.clinic_id = $1
        """
        params = [user['clinic_id']]
        
        if patient_id:
            query += f" AND pi.patient_id = ${len(params) + 1}"
            params.append(patient_id)
        
        if status:
            query += f" AND pi.status = ${len(params) + 1}"
            params.append(status)
        
        query += " ORDER BY pi.created_at DESC"
        
        invoices = await conn.fetch(query, *params)
        await conn.close()
        
        return {
            "success": True,
            "invoices": [dict(inv) for inv in invoices]
        }
    except Exception as e:
        print(f"Error fetching patient invoices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch invoices")

@app.get("/api/v1/patient-invoices/{invoice_id}")
async def get_patient_invoice(invoice_id: int, authorization: str = Header(None)):
    """Get specific patient invoice details"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        invoice = await conn.fetchrow("""
            SELECT pi.*, p.first_name, p.last_name, p.email, p.mobile_phone,
                   c.name as clinic_name, c.address_line1, c.city, c.postcode
            FROM patient_invoices pi
            JOIN patients p ON pi.patient_id = p.id
            JOIN clinics c ON pi.clinic_id = c.id
            WHERE pi.id = $1 AND pi.clinic_id = $2
        """, invoice_id, user['clinic_id'])
        
        await conn.close()
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {
            "success": True,
            "invoice": dict(invoice)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching invoice: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch invoice")

@app.post("/api/v1/patient-invoices")
async def create_patient_invoice(invoice_data: dict, authorization: str = Header(None)):
    """Create new patient invoice"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Generate invoice number
        last_invoice = await conn.fetchval("""
            SELECT invoice_number FROM patient_invoices 
            WHERE clinic_id = $1 
            ORDER BY id DESC LIMIT 1
        """, user['clinic_id'])
        
        if last_invoice:
            num = int(last_invoice.split('-')[1]) + 1
            invoice_number = f"PI-{num:05d}"
        else:
            invoice_number = "PI-00001"
        
        # Insert invoice
        invoice_id = await conn.fetchval("""
            INSERT INTO patient_invoices 
            (clinic_id, patient_id, invoice_number, amount, description, 
             service_date, due_date, status, created_by, notes)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id
        """, 
            user['clinic_id'],
            invoice_data.get('patient_id'),
            invoice_number,
            invoice_data.get('amount'),
            invoice_data.get('description'),
            invoice_data.get('service_date'),
            invoice_data.get('due_date'),
            'pending',
            user['user_id'],
            invoice_data.get('notes')
        )
        
        await conn.close()
        
        return {
            "success": True,
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "message": "Invoice created successfully"
        }
    except Exception as e:
        print(f"Error creating invoice: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create invoice")

@app.put("/api/v1/patient-invoices/{invoice_id}")
async def update_patient_invoice(
    invoice_id: int, 
    invoice_data: dict, 
    authorization: str = Header(None)
):
    """Update patient invoice"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Verify invoice belongs to clinic
        exists = await conn.fetchval("""
            SELECT id FROM patient_invoices 
            WHERE id = $1 AND clinic_id = $2
        """, invoice_id, user['clinic_id'])
        
        if not exists:
            await conn.close()
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Update invoice
        from datetime import datetime
        await conn.execute("""
            UPDATE patient_invoices
            SET amount = $1, description = $2, service_date = $3,
                due_date = $4, notes = $5, updated_at = $6
            WHERE id = $7
        """,
            invoice_data.get('amount'),
            invoice_data.get('description'),
            invoice_data.get('service_date'),
            invoice_data.get('due_date'),
            invoice_data.get('notes'),
            datetime.now(),
            invoice_id
        )
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Invoice updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating invoice: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update invoice")

@app.put("/api/v1/patient-invoices/{invoice_id}/mark-paid")
async def mark_patient_invoice_paid(invoice_id: int, authorization: str = Header(None)):
    """Mark patient invoice as paid"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Verify invoice belongs to clinic
        invoice = await conn.fetchrow("""
            SELECT id, status FROM patient_invoices
            WHERE id = $1 AND clinic_id = $2
        """, invoice_id, user['clinic_id'])
        
        if not invoice:
            await conn.close()
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Update invoice to paid
        from datetime import datetime
        await conn.execute("""
            UPDATE patient_invoices
            SET status = 'paid',
                payment_date = $1,
                paid_at = $2,
                payment_method = 'manual',
                updated_at = $2
            WHERE id = $3
        """, datetime.now().date(), datetime.now(), invoice_id)
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Invoice marked as paid"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error marking invoice paid: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update invoice")

@app.delete("/api/v1/patient-invoices/{invoice_id}")
async def delete_patient_invoice(invoice_id: int, authorization: str = Header(None)):
    """Delete/cancel patient invoice"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Mark as cancelled instead of deleting
        from datetime import datetime
        result = await conn.execute("""
            UPDATE patient_invoices
            SET status = 'cancelled', updated_at = $1
            WHERE id = $2 AND clinic_id = $3
        """, datetime.now(), invoice_id, user['clinic_id'])
        
        await conn.close()
        
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {
            "success": True,
            "message": "Invoice cancelled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error cancelling invoice: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel invoice")


        raise HTTPException(status_code=500, detail="Failed to fetch invoice")

async def get_patient(patient_id: int):
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        patient = await conn.fetchrow("""
            SELECT p.*, c.name as clinic_name 
            FROM patients p 
            LEFT JOIN clinics c ON p.clinic_id = c.id
            WHERE p.id = $1
        """, patient_id)
        
        await conn.close()
        if patient:
            return dict(patient)
        else:
            raise HTTPException(status_code=404, detail="Patient not found")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============= ASSESSMENT MODULE ENDPOINTS =============

@app.get("/api/v1/assessments/questions")
async def get_all_assessment_questions():
    """Get all assessment questions for all therapy domains"""
    return {
        "success": True,
        "questions": ASSESSMENT_QUESTIONS,
        "therapy_protocols": THERAPY_PROTOCOLS,
        "total_domains": len(ASSESSMENT_QUESTIONS)
    }

@app.get("/api/v1/assessments/questions/{domain}")
async def get_domain_questions(domain: str):
    """Get questions for a specific therapy domain"""
    if domain not in ASSESSMENT_QUESTIONS:
        raise HTTPException(
            status_code=404, 
            detail=f"Domain '{domain}' not found"
        )
    
    return {
        "success": True,
        "domain": domain,
        "domain_info": ASSESSMENT_QUESTIONS[domain],
        "total_questions": len(ASSESSMENT_QUESTIONS[domain]["questions"])
    }

@app.post("/api/v1/assessments/comprehensive")
async def create_comprehensive_assessment(assessment_data: dict):  # TODO: Convert to AssessmentCreate model
    """Create a comprehensive assessment with questionnaire and optional iridology"""
    try:
        # Convert patient_id to int (Pydantic will handle this automatically in future)
        patient_id = int(assessment_data.get("patient_id")) if assessment_data.get("patient_id") else None
        questionnaire_responses = assessment_data.get("questionnaire_responses", {})
        iris_images = assessment_data.get("iris_images", {})
        
        if not patient_id:
            raise HTTPException(status_code=400, detail="patient_id is required")
        
        # Connect to database
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Verify patient exists
        patient = await conn.fetchrow("SELECT * FROM patients WHERE id = $1", patient_id)
        if not patient:
            await conn.close()
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Calculate questionnaire scores for each domain
        questionnaire_scores = {}
        questionnaire_recommendations = {}
        
        for domain, responses in questionnaire_responses.items():
            if domain in ASSESSMENT_QUESTIONS:
                score_result = calculate_assessment_score(domain, responses)
                questionnaire_scores[domain] = score_result
                
                recommendations = generate_therapy_recommendations(domain, score_result)
                questionnaire_recommendations[domain] = recommendations
        
        # Generate multi-domain prioritized recommendations
        all_recommendations = generate_multi_domain_recommendations(questionnaire_scores)
        
        # Calculate overall wellness score
        total_score = 0
        domain_count = 0
        for domain, score_data in questionnaire_scores.items():
            if score_data.get("score", 0) > 0:
                total_score += score_data["score"]
                domain_count += 1
        
        overall_wellness_score = round(total_score / domain_count, 2) if domain_count > 0 else 0
        
        # Determine assessment status
        has_iris_images = iris_images.get('left') and iris_images.get('right')
        assessment_status = 'COMPLETED' if has_iris_images else 'questionnaire_only'
        
        # Store assessment in database
        import json
        assessment_id = await conn.fetchval(
            """INSERT INTO comprehensive_assessments 
               (patient_id, questionnaire_responses, questionnaire_scores, 
                questionnaire_recommendations, iris_images, assessment_status,
                overall_wellness_score, integrated_recommendations)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
               RETURNING id""",
            patient_id,
            json.dumps(questionnaire_responses),
            json.dumps(questionnaire_scores),
            json.dumps(questionnaire_recommendations),
            json.dumps(iris_images) if has_iris_images else None,
            assessment_status,
            overall_wellness_score,
            json.dumps(all_recommendations)
        )
        
        # Store therapy correlations
        for recommendation in all_recommendations:
            await conn.execute(
                """INSERT INTO therapy_correlations 
                   (assessment_id, therapy_code, questionnaire_priority, 
                    combined_priority, correlation_strength, recommended, recommendation_reason)
                   VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                assessment_id,
                recommendation["therapy_code"],
                recommendation["priority_level"],
                recommendation["priority_level"],
                1.0,
                recommendation["recommended"],
                recommendation["rationale"]
            )
        
        await conn.close()
        
        return {
            "success": True,
            "assessment_id": assessment_id,
            "overall_wellness_score": overall_wellness_score,
            "questionnaire_scores": questionnaire_scores,
            "recommendations": all_recommendations,
            "status": assessment_status,
            "message": "Assessment created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create assessment: {str(e)}")

@app.get("/api/v1/assessments/patient/{patient_id}")
async def get_patient_assessments(patient_id: int):
    """Get all assessments for a specific patient"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Verify patient exists
        patient = await conn.fetchrow("SELECT * FROM patients WHERE id = $1", patient_id)
        if not patient:
            await conn.close()
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get all assessments
        assessments = await conn.fetch(
            """SELECT id, patient_id, assessment_date, assessment_status,
                      overall_wellness_score, created_at
               FROM comprehensive_assessments
               WHERE patient_id = $1
               ORDER BY created_at DESC""",
            patient_id
        )
        
        await conn.close()
        
        return {
            "success": True,
            "patient_id": patient_id,
            "patient_name": f"{patient['first_name']} {patient['last_name']}",
            "patient_number": patient['patient_number'],
            "total_assessments": len(assessments),
            "assessments": [dict(a) for a in assessments]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/assessments/{assessment_id}")
async def get_assessment_details(assessment_id: int):
    """Get detailed assessment results"""
    try:
        import json
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get assessment with patient info
        assessment = await conn.fetchrow(
            """SELECT ca.*, 
                      p.first_name, p.last_name, p.patient_number, p.date_of_birth
               FROM comprehensive_assessments ca
               JOIN patients p ON ca.patient_id = p.id
               WHERE ca.id = $1""",
            assessment_id
        )
        
        if not assessment:
            await conn.close()
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Get therapy correlations
        correlations = await conn.fetch(
            """SELECT * FROM therapy_correlations 
               WHERE assessment_id = $1 
               ORDER BY 
                   CASE combined_priority 
                       WHEN 'High' THEN 1 
                       WHEN 'Moderate' THEN 2 
                       WHEN 'Low' THEN 3 
                   END""",
            assessment_id
        )
        
        await conn.close()
        
        assessment_dict = dict(assessment)
        
        # Parse JSON fields
        if assessment_dict.get('questionnaire_responses'):
            assessment_dict['questionnaire_responses'] = json.loads(assessment_dict['questionnaire_responses'])
        if assessment_dict.get('questionnaire_scores'):
            assessment_dict['questionnaire_scores'] = json.loads(assessment_dict['questionnaire_scores'])
        if assessment_dict.get('questionnaire_recommendations'):
            assessment_dict['questionnaire_recommendations'] = json.loads(assessment_dict['questionnaire_recommendations'])
        if assessment_dict.get('integrated_recommendations'):
            assessment_dict['integrated_recommendations'] = json.loads(assessment_dict['integrated_recommendations'])
        
        return {
            "success": True,
            "assessment": assessment_dict,
            "therapy_correlations": [dict(c) for c in correlations]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Import appointments endpoints


# ============================================================================
# APPOINTMENTS ENDPOINTS
# ============================================================================

@app.get("/api/v1/appointments/stats")
async def get_appointments_stats():
    """Get appointment statistics for the clinic"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        total = await conn.fetchval("SELECT COUNT(*) FROM appointments")
        today = await conn.fetchval(
            "SELECT COUNT(*) FROM appointments WHERE appointment_date = CURRENT_DATE"
        )
        scheduled = await conn.fetchval(
            "SELECT COUNT(*) FROM appointments WHERE status = 'SCHEDULED'"
        )
        this_week = await conn.fetchval(
            """
            SELECT COUNT(*) FROM appointments 
            WHERE appointment_date >= date_trunc('week', CURRENT_DATE)
            AND appointment_date < date_trunc('week', CURRENT_DATE) + interval '7 days'
            """
        )
        await conn.close()
        
        return {
            "success": True,
            "stats": {
                "total": total,
                "today": today,
                "this_week": this_week,
                "scheduled": scheduled,
                "by_status": {
                    "SCHEDULED": scheduled
                }
            }
        }
    except Exception as e:
        print(f"Error in stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/appointments/stats/overview")
async def get_appointments_stats_overview():
    """Alias for appointments stats"""
    return await get_appointments_stats()

@app.get("/api/v1/appointments")
async def get_appointments(
    status: str = None,
    date: str = None,
    patient_id: int = None
):
    """Get all appointments with optional filters"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        query = """
            SELECT 
                a.*,
                p.first_name || ' ' || p.last_name as patient_name,
                p.email as patient_email,
                p.mobile_phone as patient_phone
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            WHERE 1=1
        """
        params = []
        param_count = 1
        
        if status:
            query += f" AND a.status = ${param_count}"
            params.append(status)
            param_count += 1
            
        if date:
            query += f" AND a.appointment_date = ${param_count}"
            params.append(date)
            param_count += 1
            
        if patient_id:
            query += f" AND a.patient_id = ${param_count}"
            params.append(patient_id)
            param_count += 1
        
        query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"
        
        appointments = await conn.fetch(query, *params)
        await conn.close()
        
        return {
            "success": True,
            "appointments": [dict(a) for a in appointments]
        }
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/appointments")
async def create_appointment(appointment: AppointmentCreate):
    """Create a new appointment - Now with automatic type validation!"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )

        # Generate appointment number
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        appointment_number = f"APT-{timestamp}"

        # Convert date and time strings
        appt_date = datetime.strptime(appointment.appointment_date, "%Y-%m-%d").date()
        appt_time = datetime.strptime(appointment.appointment_time, "%H:%M").time()

        # Insert appointment - Pydantic already validated and converted types!
        appointment_id = await conn.fetchval(
            """INSERT INTO appointments (
                appointment_number, clinic_id, patient_id, appointment_type,
                appointment_date, appointment_time, duration_minutes,
                practitioner_id, status, booking_notes, created_at
            ) VALUES ($1, $2, $3, $4::appointmenttype, $5, $6, $7, $8, $9::appointmentstatus, $10, NOW())
            RETURNING id""",
            appointment_number,
            appointment.clinic_id,
            appointment.patient_id,  # Already converted to int by Pydantic!
            appointment.appointment_type,  # Already converted to enum format by Pydantic!
            appt_date,
            appt_time,
            appointment.duration_minutes,
            appointment.practitioner_id,
            'SCHEDULED',
            appointment.booking_notes
        )

        await conn.close()

        return {
            "success": True,
            "message": "Appointment created successfully",
            "appointment_id": appointment_id,
            "appointment_number": appointment_number
        }
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/appointments/{appointment_id}")
async def get_appointment(appointment_id: int):
    """Get a specific appointment by ID"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        appointment = await conn.fetchrow(
            """SELECT 
                a.*,
                p.first_name || ' ' || p.last_name as patient_name,
                p.email as patient_email,
                p.mobile_phone as patient_phone,
                p.date_of_birth as patient_dob
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            WHERE a.id = $1""",
            appointment_id
        )
        
        if not appointment:
            await conn.close()
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        await conn.close()
        
        return {
            "success": True,
            "appointment": dict(appointment)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/appointments/{appointment_id}")
async def update_appointment(appointment_id: int, appointment_data: dict):
    """Update an existing appointment"""
    from datetime import datetime, date, time
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )

        # Check if appointment exists
        exists = await conn.fetchval(
            "SELECT id FROM appointments WHERE id = $1", appointment_id
        )
        if not exists:
            await conn.close()
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Convert date/time strings to proper Python objects
        if "appointment_date" in appointment_data and isinstance(appointment_data["appointment_date"], str):
            appointment_data["appointment_date"] = datetime.strptime(appointment_data["appointment_date"], "%Y-%m-%d").date()

        if "appointment_time" in appointment_data and isinstance(appointment_data["appointment_time"], str):
            time_str = appointment_data["appointment_time"]
            if len(time_str) == 5:  # "HH:MM" format
                appointment_data["appointment_time"] = datetime.strptime(time_str, "%H:%M").time()
            else:  # "HH:MM:SS" format
                appointment_data["appointment_time"] = datetime.strptime(time_str, "%H:%M:%S").time()

        # Convert status to uppercase (enum expects UPPERCASE values)
        if "status" in appointment_data and isinstance(appointment_data["status"], str):
            appointment_data["status"] = appointment_data["status"].upper()

        # Build update query dynamically
        update_fields = []
        params = []
        param_count = 1

        allowed_fields = [
            "appointment_date", "appointment_time", "duration_minutes",
            "practitioner_id", "status", "booking_notes", "cancellation_reason"
        ]

        for field in allowed_fields:
            if field in appointment_data:
                update_fields.append(f"{field} = ${param_count}")
                params.append(appointment_data[field])
                param_count += 1
        
        if update_fields:
            update_fields.append(f"updated_at = NOW()")
            query = f"""
                UPDATE appointments 
                SET {', '.join(update_fields)}
                WHERE id = ${param_count}
            """
            params.append(appointment_id)
            
            await conn.execute(query, *params)
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Appointment updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/appointments/{appointment_id}")
async def delete_appointment(appointment_id: int):
    """Delete an appointment"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Check if appointment exists
        exists = await conn.fetchval(
            "SELECT id FROM appointments WHERE id = $1", appointment_id
        )
        if not exists:
            await conn.close()
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Delete appointment
        await conn.execute(
            "DELETE FROM appointments WHERE id = $1", appointment_id
        )
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Appointment deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/appointments/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: int, cancel_data: dict):
    """Cancel an appointment"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Update appointment status to cancelled
        await conn.execute(
            """UPDATE appointments 
               SET status = 'CANCELLED',
                   cancellation_reason = $1,
                   cancelled_at = NOW(),
                   updated_at = NOW()
               WHERE id = $2""",
            cancel_data.get("reason", "No reason provided"),
            appointment_id
        )
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Appointment cancelled successfully"
        }
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/appointments/calendar/{year}/{month}")
async def get_calendar_appointments(year: int, month: int):
    """Get appointments for a specific month (calendar view)"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        appointments = await conn.fetch(
            """SELECT 
                a.id,
                a.appointment_number,
                a.appointment_date,
                a.appointment_time,
                a.duration_minutes,
                a.status,
                a.appointment_type,
                p.first_name || ' ' || p.last_name as patient_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            WHERE EXTRACT(YEAR FROM a.appointment_date) = $1
              AND EXTRACT(MONTH FROM a.appointment_date) = $2
            ORDER BY a.appointment_date, a.appointment_time""",
            year, month
        )
        
        await conn.close()
        
        return {
            "success": True,
            "appointments": [dict(a) for a in appointments]
        }
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))




# ============================================================================
# THERAPY PLANS ENDPOINTS
# ============================================================================

@app.get("/api/v1/therapy-plans/stats")
async def get_therapy_plans_stats():
    """Get therapy plans statistics"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        total = await conn.fetchval("SELECT COUNT(*) FROM therapy_plans")
        pending = await conn.fetchval(
            "SELECT COUNT(*) FROM therapy_plans WHERE status = 'PENDING_APPROVAL'"
        )
        approved = await conn.fetchval(
            "SELECT COUNT(*) FROM therapy_plans WHERE status = 'APPROVED'"
        )
        in_progress = await conn.fetchval(
            "SELECT COUNT(*) FROM therapy_plans WHERE status = 'IN_PROGRESS'"
        )
        
        await conn.close()
        
        return {
            "total_plans": total,
            "pending_approval": pending,
            "approved_plans": approved,
            "in_progress_plans": in_progress
        }
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/therapy-plans")
async def get_therapy_plans(status: str = None, patient_id: int = None):
    """Get all therapy plans with optional filters"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        query = """
            SELECT 
                tp.*,
                p.first_name || ' ' || p.last_name as patient_name,
                p.mobile_phone as patient_phone,
                u.full_name as recommended_by_name
            FROM therapy_plans tp
            LEFT JOIN patients p ON tp.patient_id = p.id
            LEFT JOIN users u ON tp.recommended_by = u.id
            WHERE 1=1
        """
        params = []
        param_count = 1
        
        if status:
            query += f" AND tp.status = ${param_count}"
            params.append(status)
            param_count += 1
            
        if patient_id:
            query += f" AND tp.patient_id = ${param_count}"
            params.append(patient_id)
            param_count += 1
        
        query += " ORDER BY tp.created_at DESC"
        
        plans = await conn.fetch(query, *params)
        await conn.close()
        
        return {
            "success": True,
            "therapy_plans": [dict(p) for p in plans]
        }
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/therapy-plans/{plan_id}")
async def get_therapy_plan(plan_id: int):
    """Get a specific therapy plan with items"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get plan details
        plan = await conn.fetchrow(
            """SELECT 
                tp.*,
                p.first_name || ' ' || p.last_name as patient_name,
                p.mobile_phone as patient_phone,
                u.full_name as recommended_by_name
            FROM therapy_plans tp
            LEFT JOIN patients p ON tp.patient_id = p.id
            LEFT JOIN users u ON tp.recommended_by = u.id
            WHERE tp.id = $1""",
            plan_id
        )
        
        if not plan:
            await conn.close()
            raise HTTPException(status_code=404, detail="Therapy plan not found")
        
        # Get plan items
        items = await conn.fetch(
            """SELECT * FROM therapy_plan_items 
               WHERE therapy_plan_id = $1 
               ORDER BY 
                   CASE priority
                       WHEN 'PRIMARY' THEN 1
                       WHEN 'SECONDARY' THEN 2
                       WHEN 'SUPPLEMENTARY' THEN 3
                   END""",
            plan_id
        )
        
        await conn.close()
        
        return {
            "success": True,
            "therapy_plan": dict(plan),
            "items": [dict(i) for i in items]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/therapy-plans")
async def create_therapy_plan(plan_data: dict):
    """Create a new therapy plan"""
    try:
        from datetime import datetime
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Generate plan number
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        plan_number = f"TP-{timestamp}"
        
        # Insert therapy plan - Convert IDs to integers
        plan_id = await conn.fetchval(
            """INSERT INTO therapy_plans (
                plan_number, clinic_id, patient_id, assessment_id,
                recommended_by, status, notes, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
            RETURNING id""",
            plan_number,
            int(plan_data.get("clinic_id", 1)),
            int(plan_data["patient_id"]),
            int(plan_data["assessment_id"]),
            int(plan_data.get("recommended_by", 1)),
            "PENDING_APPROVAL",
            plan_data.get("notes")
        )
        
        # Insert therapy plan items
        if "items" in plan_data and plan_data["items"]:
            for item in plan_data["items"]:
                await conn.execute(
                    """INSERT INTO therapy_plan_items (
                        therapy_plan_id, therapy_code, therapy_name,
                        therapy_description, recommended_sessions,
                        session_duration_minutes, rationale,
                        target_domain, priority, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())""",
                    plan_id,
                    item["therapy_code"],
                    item["therapy_name"],
                    item.get("therapy_description"),
                    item["recommended_sessions"],
                    item.get("session_duration_minutes", 60),
                    item.get("rationale"),
                    item.get("target_domain"),
                    item.get("priority", "PRIMARY")
                )
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Therapy plan created successfully",
            "plan_id": plan_id,
            "plan_number": plan_number
        }
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/therapy-plans/{plan_id}/status")
async def update_therapy_plan_status(plan_id: int, status_data: dict):
    """Update therapy plan status"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        await conn.execute(
            """UPDATE therapy_plans 
               SET status = $1, updated_at = NOW()
               WHERE id = $2""",
            status_data["status"],
            plan_id
        )
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Status updated successfully"
        }
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))




# ============================================================================
# REPORTS ENDPOINTS
# ============================================================================

@app.get("/api/v1/reports/overview")
async def get_reports_overview():
    """Get overall system statistics"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get counts
        total_patients = await conn.fetchval("SELECT COUNT(*) FROM patients")
        active_patients = await conn.fetchval(
            "SELECT COUNT(*) FROM patients WHERE status = 'active'"
        )
        total_assessments = await conn.fetchval(
            "SELECT COUNT(*) FROM comprehensive_assessments"
        )
        total_appointments = await conn.fetchval("SELECT COUNT(*) FROM appointments")
        total_therapy_plans = await conn.fetchval("SELECT COUNT(*) FROM therapy_plans")
        
        # Appointments by status
        appointments_by_status = await conn.fetch(
            "SELECT status, COUNT(*) as count FROM appointments GROUP BY status"
        )
        
        # Therapy plans by status
        plans_by_status = await conn.fetch(
            "SELECT status, COUNT(*) as count FROM therapy_plans GROUP BY status"
        )
        
        # Average wellness scores
        avg_wellness = await conn.fetchval(
            """SELECT AVG(overall_wellness_score) 
               FROM comprehensive_assessments 
               WHERE overall_wellness_score > 0"""
        )
        
        # Recent activity
        recent_assessments = await conn.fetchval(
            """SELECT COUNT(*) FROM comprehensive_assessments 
               WHERE assessment_date >= NOW() - INTERVAL '30 days'"""
        )
        
        recent_appointments = await conn.fetchval(
            """SELECT COUNT(*) FROM appointments 
               WHERE created_at >= NOW() - INTERVAL '30 days'"""
        )
        
        await conn.close()
        
        return {
            "success": True,
            "overview": {
                "patients": {
                    "total": total_patients,
                    "active": active_patients
                },
                "assessments": {
                    "total": total_assessments,
                    "recent_30_days": recent_assessments,
                    "avg_wellness_score": round(float(avg_wellness or 0), 2)
                },
                "appointments": {
                    "total": total_appointments,
                    "recent_30_days": recent_appointments,
                    "by_status": {row['status']: row['count'] for row in appointments_by_status}
                },
                "therapy_plans": {
                    "total": total_therapy_plans,
                    "by_status": {row['status']: row['count'] for row in plans_by_status}
                }
            }
        }
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/reports/patient-activity")
async def get_patient_activity():
    """Get patient activity report"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Patient activity with assessment and appointment counts
        activity = await conn.fetch("""
            SELECT 
                p.id,
                p.first_name || ' ' || p.last_name as patient_name,
                p.mobile_phone,
                p.email,
                p.status,
                COUNT(DISTINCT ca.id) as assessment_count,
                COUNT(DISTINCT a.id) as appointment_count,
                COUNT(DISTINCT tp.id) as therapy_plan_count,
                MAX(ca.assessment_date) as last_assessment_date,
                MAX(a.appointment_date) as last_appointment_date
            FROM patients p
            LEFT JOIN comprehensive_assessments ca ON p.id = ca.patient_id
            LEFT JOIN appointments a ON p.id = a.patient_id
            LEFT JOIN therapy_plans tp ON p.id = tp.patient_id
            GROUP BY p.id, p.first_name, p.last_name, p.mobile_phone, p.email, p.status
            ORDER BY p.id DESC
        """)
        
        await conn.close()
        
        return {
            "success": True,
            "patient_activity": [dict(row) for row in activity]
        }
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/reports/wellness-trends")
async def get_wellness_trends():
    """Get wellness score trends over time"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Monthly wellness trends
        trends = await conn.fetch("""
            SELECT 
                DATE_TRUNC('month', assessment_date) as month,
                AVG(overall_wellness_score) as avg_score,
                COUNT(*) as assessment_count
            FROM comprehensive_assessments
            WHERE overall_wellness_score > 0
            GROUP BY DATE_TRUNC('month', assessment_date)
            ORDER BY month DESC
            LIMIT 12
        """)
        
        await conn.close()
        
        return {
            "success": True,
            "wellness_trends": [dict(row) for row in trends]
        }
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/health")
async def health():
    return {"status": "healthy"}

# ============================================================================
# INVITATION API - Email System
# ============================================================================
import sys
import os

backend_dir = "/var/www/celloxen-portal/backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    import invitation_api
    app.include_router(invitation_api.router)
    print("✅ Invitation API loaded successfully")
except Exception as e:
    print(f"⚠️ Could not load invitation API: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# REGISTRATION API - Public registration endpoints
# ============================================================================
try:
    import registration_api
    app.include_router(registration_api.router)
    print("✅ Registration API loaded successfully")
except Exception as e:
    print(f"⚠️ Could not load registration API: {e}")
    import traceback
    traceback.print_exc()

# ==========================================
# CHATBOT ASSESSMENT MODULE INTEGRATION
# ==========================================
try:
    app.include_router(chatbot_router, prefix="/api/v1", tags=["chatbot"])
    print("✅ Chatbot Assessment API loaded successfully")

except Exception as e:
    print(f"⚠️ Warning: Could not load Chatbot API: {e}")

# Add this endpoint to simple_auth_main.py

    print(f"⚠️ Warning: Could not load Chatbot API: {e}")
@app.get("/api/v1/patients/{patient_id}/assessment-overview")
async def get_patient_assessment_overview(patient_id: int, authorization: str = Header(None)):
    """Get complete assessment overview for a patient"""
    try:
        # Simple token check
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get latest assessment
        latest_assessment = await conn.fetchrow("""
            SELECT * FROM assessments 
            WHERE patient_id = $1 
            ORDER BY created_at DESC LIMIT 1
        """, patient_id)
        
        # Get chatbot session if exists
        chatbot_session = await conn.fetchrow("""
            SELECT * FROM chatbot_sessions 
            WHERE patient_id = $1 
            ORDER BY created_at DESC LIMIT 1
        """, patient_id)
        
        await conn.close()
        
        if not latest_assessment:
            return {
                "has_assessment": False,
                "assessment_id": None,
                "assessment_date": None,
                "overall_score": 0,
                "domain_scores": {
                    "energy": 0, "digestion": 0, "stress": 0, "metabolism": 0, "sleep": 0
                },
                "progress_percentage": 0,
                "chatbot_session": None,
                "status": {
                    "questionnaire": "pending",
                    "chat": "pending",
                    "iridology": "pending",
                    "analysis": "pending",
                    "report": "pending"
                }
            }
        
        # Calculate progress
        progress = 20  # Questionnaire complete
        if chatbot_session and chatbot_session['current_stage'] == 'iridology_prep':
            progress = 40
        
        return {
            "has_assessment": True,
            "assessment_id": latest_assessment['id'],
            "assessment_date": str(latest_assessment['created_at']),
            "overall_score": float(latest_assessment['overall_score']) if latest_assessment['overall_score'] else 0,
            "domain_scores": {
                "energy": float(latest_assessment['energy_score']) if latest_assessment['energy_score'] else 0,
                "digestion": float(latest_assessment['digestion_score']) if latest_assessment['digestion_score'] else 0,
                "stress": float(latest_assessment['stress_score']) if latest_assessment['stress_score'] else 0,
                "metabolism": float(latest_assessment['metabolism_score']) if latest_assessment['metabolism_score'] else 0,
                "sleep": float(latest_assessment['sleep_score']) if latest_assessment['sleep_score'] else 0
            },
            "progress_percentage": progress,
            "chatbot_session": dict(chatbot_session) if chatbot_session else None,
            "status": {
                "questionnaire": "complete",
                "chat": "complete" if chatbot_session else "pending",
                "iridology": "pending",
                "analysis": "pending",
                "report": "pending"
            }
        }
        
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# IRIDOLOGY & REPORT ENDPOINTS
# Add these to simple_auth_main.py
# ============================================

@app.post("/api/v1/assessments/{assessment_id}/iridology")
async def add_iridology_to_assessment(assessment_id: int, iridology_data: dict):
    """Add AI-powered iridology analysis to existing assessment"""
    try:
        left_eye_image = iridology_data.get("left_eye_image")
        right_eye_image = iridology_data.get("right_eye_image")
        patient_info = iridology_data.get("patient_info", {})
        
        if not ai_analyzer:
            return {"success": False, "error": "AI analyzer not configured - check ANTHROPIC_API_KEY"}
        
        if not left_eye_image or not right_eye_image:
            return {"success": False, "error": "Both eye images are required"}
        
        # Perform AI analysis
        print(f"Starting iridology analysis for assessment {assessment_id}")
        analysis_result = await ai_analyzer.analyze_iris_images(
            left_eye_image,
            right_eye_image,
            patient_info
        )
        
        if not analysis_result.get("success"):
            return {"success": False, "error": analysis_result.get("error", "Analysis failed")}
        
        print(f"AI analysis completed successfully")
        
        # Update assessment in database
        async with get_db_connection() as conn:
            # Update comprehensive_assessments
            await conn.execute(
                """UPDATE comprehensive_assessments 
                   SET iridology_data = $1,
                       constitutional_type = $2,
                       constitutional_strength = $3,
                       iris_images = $4,
                       assessment_status = 'completed',
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = $5""",
                json.dumps(analysis_result),
                analysis_result["combined_analysis"].get("constitutional_type", "Unknown"),
                analysis_result["combined_analysis"].get("constitutional_strength", "Unknown"),
                json.dumps({
                    "left_eye": "stored",
                    "right_eye": "stored",
                    "timestamp": str(datetime.now())
                }),
                assessment_id
            )
            
            # Store detailed findings in iridology_findings table
            systems = analysis_result["combined_analysis"].get("systems", {})
            
            await conn.execute(
                """INSERT INTO iridology_findings 
                   (assessment_id, left_eye_constitutional, right_eye_constitutional,
                    constitutional_notes, digestive_system_condition, circulatory_system_condition,
                    nervous_system_condition, musculoskeletal_system_condition, endocrine_system_condition,
                    iris_signs, primary_concerns, wellness_priorities)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)""",
                assessment_id,
                analysis_result["left_eye_findings"].get("constitutional_type", "Unknown"),
                analysis_result["right_eye_findings"].get("constitutional_type", "Unknown"),
                "AI-powered analysis completed",
                systems.get("digestive", "Good"),
                systems.get("circulatory", "Good"),
                systems.get("nervous", "Good"),
                systems.get("musculoskeletal", "Good"),
                systems.get("endocrine", "Good"),
                json.dumps(analysis_result.get("combined_analysis", {}).get("iris_signs", [])),
                analysis_result["combined_analysis"].get("primary_concerns", []),
                analysis_result["combined_analysis"].get("wellness_priorities", [])
            )
        
        print(f"Database updated successfully")
        
        return {
            "success": True,
            "assessment_id": assessment_id,
            "analysis": analysis_result["combined_analysis"],
            "message": "Iridology analysis completed and stored successfully"
        }
        
    except Exception as e:
        print(f"Error in iridology endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


@app.get("/api/v1/assessments/{assessment_id}/complete")
async def get_complete_assessment(assessment_id: int):
    """Get complete assessment including questionnaire and iridology"""
    try:
        async with get_db_connection() as conn:
            # Get main assessment
            assessment = await conn.fetchrow(
                """SELECT ca.*, 
                          p.first_name, p.last_name, p.date_of_birth, p.patient_number,
                          u.full_name as practitioner_name
                   FROM comprehensive_assessments ca
                   JOIN patients p ON ca.patient_id = p.id
                   LEFT JOIN users u ON ca.practitioner_id = u.id
                   WHERE ca.id = $1""",
                assessment_id
            )
            
            if not assessment:
                return {"success": False, "error": "Assessment not found"}
            
            # Get iridology findings
            iridology = await conn.fetchrow(
                "SELECT * FROM iridology_findings WHERE assessment_id = $1",
                assessment_id
            )
            
            # Convert to dicts
            assessment_dict = dict(assessment)
            
            # Parse JSON fields
            if assessment_dict.get('questionnaire_scores'):
                if isinstance(assessment_dict['questionnaire_scores'], str):
                    assessment_dict['questionnaire_scores'] = json.loads(assessment_dict['questionnaire_scores'])
            
            if assessment_dict.get('iridology_data'):
                if isinstance(assessment_dict['iridology_data'], str):
                    assessment_dict['iridology_data'] = json.loads(assessment_dict['iridology_data'])
            
            return {
                "success": True,
                "assessment": assessment_dict,
                "iridology_findings": dict(iridology) if iridology else None,
                "has_complete_analysis": assessment["assessment_status"] == "completed",
                "has_iridology": iridology is not None
            }
            
    except Exception as e:
        print(f"Error fetching complete assessment: {str(e)}")
        return {"success": False, "error": str(e)}


@app.get("/api/v1/assessments/{assessment_id}/report")
async def generate_assessment_report(assessment_id: int):
    """Generate comprehensive PDF report"""
    try:
        async with get_db_connection() as conn:
            # Get assessment data
            assessment = await conn.fetchrow(
                "SELECT * FROM comprehensive_assessments WHERE id = $1",
                assessment_id
            )
            
            if not assessment:
                return {"success": False, "error": "Assessment not found"}
            
            # Get patient data
            patient = await conn.fetchrow(
                "SELECT * FROM patients WHERE id = $1",
                assessment['patient_id']
            )
            
            # Get iridology data
            iridology = await conn.fetchrow(
                "SELECT * FROM iridology_findings WHERE assessment_id = $1",
                assessment_id
            )
            
            # Convert to dicts and parse JSON
            assessment_dict = dict(assessment)
            patient_dict = dict(patient)
            
            # Parse JSON fields
            if assessment_dict.get('questionnaire_scores'):
                if isinstance(assessment_dict['questionnaire_scores'], str):
                    assessment_dict['questionnaire_scores'] = json.loads(assessment_dict['questionnaire_scores'])
            
            if assessment_dict.get('questionnaire_recommendations'):
                if isinstance(assessment_dict['questionnaire_recommendations'], str):
                    assessment_dict['questionnaire_recommendations'] = json.loads(assessment_dict['questionnaire_recommendations'])
            
            if assessment_dict.get('integrated_recommendations'):
                if isinstance(assessment_dict['integrated_recommendations'], str):
                    assessment_dict['integrated_recommendations'] = json.loads(assessment_dict['integrated_recommendations'])
            
            # Add recommendations to assessment dict - use integrated_recommendations if available
            if 'recommendations' not in assessment_dict:
                if assessment_dict.get('integrated_recommendations'):
                    assessment_dict['recommendations'] = assessment_dict['integrated_recommendations']
                elif assessment_dict.get('questionnaire_recommendations'):
                    assessment_dict['recommendations'] = assessment_dict['questionnaire_recommendations']
            
            # Generate PDF
            pdf_buffer = report_generator.generate_comprehensive_report(
                assessment_dict,
                patient_dict,
                dict(iridology) if iridology else None
            )
            
            # Return as downloadable PDF
            return StreamingResponse(
                pdf_buffer,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=celloxen_assessment_{assessment_id}_report.pdf"
                }
            )
            
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


# Import iridology module
from ai_iridology_module import router as iridology_router
app.include_router(iridology_router)

# Import report generator
from report_generator import generate_wellness_report
from iridology_pdf_generator import generate_iridology_pdf

@app.post("/api/v1/reports/generate/{assessment_id}")
async def generate_report_endpoint(assessment_id: int):
    """Generate wellness report PDF"""
    try:
        pdf_path = await generate_wellness_report(assessment_id)
        
        # Return download link
        filename = pdf_path.split('/')[-1]
        return {
            "success": True,
            "assessment_id": assessment_id,
            "report_path": pdf_path,
            "download_url": f"/reports/{filename}"
        }
    except Exception as e:
        import traceback
        print(f"ERROR generating report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/{filename}")
async def download_report(filename: str):
    """Download generated report"""
    from fastapi.responses import FileResponse
    import os
    
    file_path = f"/var/www/celloxen-portal/reports/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        file_path,
        media_type='application/pdf',
        filename=filename
    )

# ==================== NEW ASSESSMENT DASHBOARD ENDPOINT ====================

# ==================== ASSESSMENT DASHBOARD ENDPOINT ====================
@app.get("/api/v1/assessments/patient/{patient_id}/dashboard")
async def get_patient_assessment_dashboard(
    patient_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get complete assessment dashboard data for a patient"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get patient info
        patient = await conn.fetchrow("""
            SELECT id, patient_number, first_name, last_name, email, date_of_birth
            FROM patients WHERE id = $1
        """, patient_id)
        
        if not patient:
            await conn.close()
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get latest assessment
        assessment = await conn.fetchrow("""
            SELECT * FROM comprehensive_assessments 
            WHERE patient_id = $1 
            ORDER BY created_at DESC LIMIT 1
        """, patient_id)
        
        await conn.close()
        
        # Calculate progress
        progress = 0
        modules = {"questionnaire": False, "iridology": False, "analysis": False, "report": False}
        
        if assessment:
            if assessment.get('questionnaire_completed'):
                modules["questionnaire"] = True
                progress = 25
            if assessment.get('iridology_completed'):
                modules["iridology"] = True
                modules["analysis"] = True
                progress = 75
            if assessment.get('comprehensive_report'):
                modules["report"] = True
                progress = 100
        
        # Parse domain scores - handle both old and new field names
        domain_scores = {"energy": 0, "comfort": 0, "circulation": 0, "stress": 0, "metabolic": 0}
        
        if assessment and assessment.get("questionnaire_scores"):
            import json
            scores = assessment["questionnaire_scores"]
            if isinstance(scores, str):
                scores = json.loads(scores)
            
            # Handle both formats: old (vitality_energy) and new (c102_vitality_energy)
            def get_score(scores, old_key, new_key):
                if old_key in scores and isinstance(scores[old_key], dict):
                    return scores[old_key].get("score", 0)
                elif new_key in scores:
                    return scores.get(new_key, 0)
                return 0
            
            # Convert percentage scores to 0-7 scale for dials
            domain_scores = {
                "energy": round(get_score(scores, "vitality_energy", "c102_vitality_energy") / 100 * 7, 2),
                "comfort": round(get_score(scores, "comfort_mobility", "c104_comfort_mobility") / 100 * 7, 2),
                "circulation": round(get_score(scores, "circulation_heart", "c105_circulation_heart") / 100 * 7, 2),
                "stress": round(get_score(scores, "stress_relaxation", "c107_stress_relaxation") / 100 * 7, 2),
                "metabolic": round(get_score(scores, "immune_digestive", "c108_metabolic_balance") / 100 * 7, 2)
            }
        
        return {
            "success": True,
            "patient": {
                "id": patient['id'],
                "patient_number": patient['patient_number'],
                "name": f"{patient['first_name']} {patient['last_name']}",
                "email": patient['email']
            },
            "assessment": {
                "id": assessment['id'] if assessment else None,
                "overall_score": float(assessment['overall_wellness_score']) if assessment and assessment.get('overall_wellness_score') else 0,
                "progress": progress,
                "modules_completed": modules
            },
            "domain_scores": domain_scores,
            "has_iridology": assessment.get('iridology_completed') if assessment else False
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ==================== SIMPLE ASSESSMENT MODULE ====================
from simple_assessment_api import router as assessment_router
app.include_router(assessment_router)
print("✅ Simple Assessment API loaded successfully")

# ============================================

# ============================================
# IRIDOLOGY MODULE API ENDPOINTS (FIXED)
# ============================================

from iridology_analyzer import IridologyAnalyzer
import asyncpg

# Initialize analyzer (will use ANTHROPIC_API_KEY from environment)
iridology_analyzer = IridologyAnalyzer()

@app.post("/api/v1/iridology/start")
async def start_iridology_analysis(
    patient_id: int,
    disclaimer_accepted: bool,
    current_user: dict = Depends(get_current_user)
):
    """Start new iridology analysis session"""
    
    if not disclaimer_accepted:
        raise HTTPException(status_code=400, detail="Disclaimer must be accepted")
    
    try:
        # Create database connection
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        try:
            # Get patient details
            patient = await conn.fetchrow(
                "SELECT * FROM patients WHERE id = $1",
                patient_id
            )
            
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")
            
            # Create analysis record
            analysis_id = await conn.fetchval(
                """
                INSERT INTO iridology_analyses (
                    patient_id, practitioner_id, clinic_id,
                    disclaimer_accepted, disclaimer_accepted_at,
                    disclaimer_text, status,
                    left_eye_image, right_eye_image, capture_method
                ) VALUES ($1, $2, $3, $4, NOW(), $5, 'pending', '', '', 'upload')
                RETURNING id
                """,
                patient_id,
                current_user["id"],
                1,
                disclaimer_accepted,
                """This iridology analysis is a holistic wellness assessment tool and is NOT intended as medical diagnosis. 
                The iris analysis provides insights into potential wellness patterns and areas that may benefit from lifestyle support. 
                This analysis does NOT diagnose medical conditions, replace medical consultation, or prescribe treatments. 
                If the analysis identifies patterns that may indicate health concerns, we strongly recommend consulting your GP."""
            )
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "patient": {
                    "id": patient["id"],
                    "first_name": patient["first_name"],
                    "last_name": patient["last_name"],
                    "patient_number": patient["patient_number"],
                    "date_of_birth": patient["date_of_birth"].isoformat() if patient.get("date_of_birth") else None
                }
            }
            
        finally:
            await conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/iridology/{analysis_id}/upload-images")
async def upload_iris_images(
    analysis_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Upload iris images for analysis"""
    
    # Get JSON body
    body = await request.json()
    left_eye_image = body.get('left_eye_image')
    right_eye_image = body.get('right_eye_image')
    capture_method = body.get('capture_method')
    
    if capture_method not in ["camera", "upload"]:
        raise HTTPException(status_code=400, detail="Invalid capture method")
    
    if not left_eye_image or not right_eye_image:
        raise HTTPException(status_code=400, detail="Both eye images required")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        try:
            # Update analysis with images
            await conn.execute(
                """
                UPDATE iridology_analyses 
                SET left_eye_image = $1, 
                    right_eye_image = $2,
                    capture_method = $3,
                    status = 'pending',
                    updated_at = NOW()
                WHERE id = $4
                """,
                left_eye_image,
                right_eye_image,
                capture_method,
                analysis_id)
            
            return {
                "success": True,
                "message": "Images uploaded successfully",
                "analysis_id": analysis_id
            }
            
        finally:
            await conn.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/iridology/{analysis_id}/analyse")
async def analyse_iris_images(
    analysis_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Trigger Claude AI analysis of iris images"""
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        try:
            # Get analysis record
            analysis = await conn.fetchrow(
                """
                SELECT ia.*, p.first_name, p.last_name, p.date_of_birth, p.gender
                FROM iridology_analyses ia
                JOIN patients p ON ia.patient_id = p.id
                WHERE ia.id = $1
                """,
                analysis_id,
            )
            
            if not analysis:
                raise HTTPException(status_code=404, detail="Analysis not found")
            
            if not analysis["left_eye_image"] or not analysis["right_eye_image"]:
                raise HTTPException(status_code=400, detail="Images not uploaded")
            
            # Update status to processing
            await conn.execute(
                """
                UPDATE iridology_analyses 
                SET status = 'processing', 
                    processing_started_at = NOW(),
                    updated_at = NOW()
                WHERE id = $1
                """,
                analysis_id
            )
            
            # Prepare patient info
            from datetime import date
            age = None
            if analysis["date_of_birth"]:
                age = (date.today() - analysis["date_of_birth"]).days // 365
            
            patient_info = {
                "name": f"{analysis['first_name']} {analysis['last_name']}",
                "age": age,
                "gender": analysis.get("gender", "Unknown")
            }
            
            # Run AI analysis
            result = await iridology_analyzer.analyse_bilateral(
                analysis["left_eye_image"],
                analysis["right_eye_image"],
                patient_info
            )
            
            if not result["success"]:
                # Mark as failed
                await conn.execute(
                    """
                    UPDATE iridology_analyses 
                    SET status = 'failed',
                        error_message = $1,
                        updated_at = NOW()
                    WHERE id = $2
                    """,
                    result.get("error", "Analysis failed"),
                    analysis_id
                )
                raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
            
            # Extract results
            combined = result.get("combined_analysis", {})
            const_type = combined.get("constitutional_type", "Unknown")
            const_strength = combined.get("constitutional_strength", "Unknown")
            
            # Update analysis with results
            await conn.execute(
                """
                UPDATE iridology_analyses 
                SET status = 'completed',
                    constitutional_type = $1,
                    constitutional_strength = $2,
                    ai_confidence_score = $3,
                    left_eye_analysis = $4,
                    right_eye_analysis = $5,
                    combined_analysis = $6,
                    processing_completed_at = NOW(),
                    updated_at = NOW()
                WHERE id = $7
                """,
                const_type,
                const_strength,
                result.get("confidence_score", 0),
                json.dumps(result.get("left_eye_analysis", {})),
                json.dumps(result.get("right_eye_analysis", {})),
                json.dumps(combined),
                analysis_id
            )
            
            # Store therapy recommendations
            therapy_priorities = combined.get("therapy_priorities", [])
            for therapy in therapy_priorities:
                await conn.execute(
                    """
                    INSERT INTO iridology_therapy_recommendations (
                        analysis_id, therapy_code, therapy_name, priority_level,
                        recommendation_reason, expected_benefits,
                        diabetes_specific
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    analysis_id,
                    therapy.get("code", ""),
                    therapy.get("name", ""),
                    therapy.get("priority", 5),
                    therapy.get("reason", ""),
                    therapy.get("expected_benefits", ""),
                    therapy.get("diabetes_specific", False)
                )
            
            # Check if GP consultation recommended
            gp_summary = combined.get("gp_consultation_summary", {})
            if gp_summary.get("recommended"):
                await conn.execute(
                    """
                    UPDATE iridology_analyses 
                    SET gp_referral_recommended = true,
                        gp_referral_reason = $1
                    WHERE id = $2
                    """,
                    ", ".join(gp_summary.get("reasons", [])),
                    analysis_id
                )
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "constitutional_type": const_type,
                "constitutional_strength": const_strength,
                "confidence_score": result.get("confidence_score", 0),
                "gp_consultation_recommended": gp_summary.get("recommended", False)
            }
            
        finally:
            await conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        # Mark as failed
        try:
            conn2 = await asyncpg.connect(
                host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
            )
            await conn2.execute(
                """
                UPDATE iridology_analyses 
                SET status = 'failed',
                    error_message = $1,
                    updated_at = NOW()
                WHERE id = $2
                """,
                str(e),
                analysis_id
            )
            await conn2.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/iridology/{analysis_id}/results")
async def get_iridology_results(
    analysis_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get complete iridology analysis results"""
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        try:
            # Get analysis
            analysis = await conn.fetchrow(
                """
                SELECT ia.*, p.first_name, p.last_name, p.patient_number
                FROM iridology_analyses ia
                JOIN patients p ON ia.patient_id = p.id
                WHERE ia.id = $1
                """,
                analysis_id)
            
            if not analysis:
                raise HTTPException(status_code=404, detail="Analysis not found")
            
            # Get therapy recommendations
            therapies = await conn.fetch(
                """
                SELECT * FROM iridology_therapy_recommendations
                WHERE analysis_id = $1
                ORDER BY priority_level
                """,
                analysis_id
            )
            
            return {
                "success": True,
                "patient": {
                    "first_name": analysis["first_name"],
                    "last_name": analysis["last_name"],
                    "patient_number": analysis["patient_number"]
                },
                "analysis": {
                    "id": analysis["id"],
                    "analysis_number": analysis["analysis_number"],
                    "constitutional_type": analysis["constitutional_type"],
                    "constitutional_strength": analysis["constitutional_strength"],
                    "confidence_score": float(analysis["ai_confidence_score"]) if analysis["ai_confidence_score"] else 0,
                    "status": analysis["status"],
                    "combined_analysis": json.loads(analysis["combined_analysis"]) if analysis["combined_analysis"] else {},
                    "gp_referral_recommended": analysis["gp_referral_recommended"],
                    "gp_referral_reason": analysis["gp_referral_reason"],
                    "created_at": analysis["created_at"].isoformat()
                },
                "therapy_recommendations": [
                    {
                        "code": t["therapy_code"],
                        "name": t["therapy_name"],
                        "priority": t["priority_level"],
                        "reason": t["recommendation_reason"],
                        "expected_benefits": t["expected_benefits"],
                        "diabetes_specific": t["diabetes_specific"]
                    }
                    for t in therapies
                ]
            }
            
        finally:
            await conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/iridology/{analysis_id}/download-pdf")
async def download_iridology_pdf(
    analysis_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Download iridology analysis as PDF report"""
    try:
        from fastapi.responses import Response
        
        # Generate PDF
        pdf_bytes = await generate_iridology_pdf(analysis_id)
        
        # Return as downloadable file
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=iridology_report_{analysis_id}.pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/iridology/{analysis_id}/report")
async def view_iridology_report(
    analysis_id: int,
    current_user: dict = Depends(get_current_user)
):
    """View iridology analysis report in browser"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        try:
            # Get analysis with patient info
            analysis = await conn.fetchrow("""
                SELECT
                    ia.*,
                    p.first_name, p.last_name, p.patient_number, p.date_of_birth
                FROM iridology_analyses ia
                JOIN patients p ON ia.patient_id = p.id
                WHERE ia.id = $1
            """, analysis_id)
            
            if not analysis:
                raise HTTPException(status_code=404, detail="Analysis not found")
            
            # Return report data
            return {
                "success": True,
                "patient": {
                    "name": f"{analysis['first_name']} {analysis['last_name']}",
                    "patient_number": analysis['patient_number'],
                    "date_of_birth": str(analysis['date_of_birth']) if analysis['date_of_birth'] else None
                },
                "analysis": {
                    "id": analysis['id'],
                    "analysis_number": analysis['analysis_number'],
                    "date": analysis['created_at'].strftime('%d %B %Y'),
                    "constitutional_type": analysis['constitutional_type'],
                    "constitutional_strength": analysis['constitutional_strength'],
                    "confidence_score": float(analysis['ai_confidence_score']) if analysis['ai_confidence_score'] else 0,
                    "gp_referral_recommended": analysis['gp_referral_recommended'],
                    "gp_referral_reason": analysis['gp_referral_reason']
                },
                "report_text": json.loads(analysis["combined_analysis"]).get("raw_text", "") if analysis["combined_analysis"] else ""
            }
        finally:
            await conn.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Recent Iridology Analyses Endpoint
@app.get("/api/v1/iridology/recent")
async def get_recent_iridology_analyses(
    limit: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """Get recent iridology analyses for current practitioner"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )

        try:
            analyses = await conn.fetch(
                """
                SELECT 
                    ia.id,
                    ia.analysis_number,
                    ia.status,
                    ia.created_at,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.patient_number
                FROM iridology_analyses ia
                JOIN patients p ON ia.patient_id = p.id
                WHERE ia.practitioner_id = $1
                ORDER BY ia.created_at DESC
                LIMIT $2
                """,
                current_user["id"],
                limit
            )

            return {
                "success": True,
                "analyses": [
                    {
                        "id": a["id"],
                        "analysis_number": a["analysis_number"],
                        "patient_name": a["patient_name"],
                        "patient_number": a["patient_number"],
                        "status": a["status"],
                        "created_at": a["created_at"].strftime("%d %b %Y %H:%M")
                    }
                    for a in analyses
                ]
            }
        finally:
            await conn.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PATIENT APPOINTMENT BOOKING
# ============================================================================

@app.get("/api/v1/patient/available-slots")
async def get_available_appointment_slots(
    date: str = None,
    authorization: str = Header(None)
):
    """Get available appointment slots for booking - PATIENT ACCESS"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization token")
    
    try:
        # Extract patient_id from JWT token
        import jwt
        token = authorization.replace("Bearer ", "")
        
        try:
            # Decode JWT token
            decoded = jwt.decode(token, options={"verify_signature": False})
            patient_id = int(decoded.get("sub"))
        except:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get clinic_id from patient record
        conn_temp = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        patient_info = await conn_temp.fetchrow(
            "SELECT clinic_id FROM patients WHERE id = $1", patient_id
        )
        
        await conn_temp.close()
        
        if not patient_info:
            raise HTTPException(status_code=403, detail="Patient not found")
        
        clinic_id = patient_info['clinic_id']
        
        from datetime import datetime, timedelta
        
        # Default to next 7 days if no date specified
        if not date:
            start_date = datetime.now().date()
        else:
            start_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        end_date = start_date + timedelta(days=7)
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get practitioners from this clinic
        practitioners = await conn.fetch("""
            SELECT id, full_name FROM users 
            WHERE clinic_id = $1 
            AND role IN ('clinic_admin', 'clinic_user')
            AND status = 'active'
        """, clinic_id)
        
        # Generate available slots (9 AM to 5 PM, hourly)
        available_slots = []
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends (optional)
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                for hour in range(9, 17):  # 9 AM to 5 PM
                    from datetime import time as dt_time
                    time_slot = dt_time(hour, 0, 0)  # Create proper time object
                    time_slot_str = f"{hour:02d}:00:00"
                    
                    # Check if slot is already booked
                    existing = await conn.fetchval("""
                        SELECT COUNT(*) FROM appointments
                        WHERE appointment_date = $1
                        AND appointment_time = $2
                        AND clinic_id = $3
                        AND status != 'CANCELLED'
                    """, current_date, time_slot, clinic_id)
                    
                    if existing == 0:
                        available_slots.append({
                            "date": str(current_date),
                            "time": time_slot_str,
                            "available": True
                        })
            
            current_date += timedelta(days=1)
        
        await conn.close()
        
        return {
            "success": True,
            "practitioners": [{"id": p['id'], "name": p['full_name']} for p in practitioners],
            "available_slots": available_slots[:20]  # Limit to 20 slots
        }
        
    except Exception as e:
        print(f"Available slots error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get available slots")


@app.post("/api/v1/patient/book-appointment")
async def book_patient_appointment(data: dict, authorization: str = Header(None)):
    """Book appointment - PATIENT SELF-BOOKING"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization token")
    
    try:
        # Extract patient info from token
        # Extract patient_id from JWT token
        import jwt
        token = authorization.replace("Bearer ", "")
        
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            patient_id = int(decoded.get("sub"))
        except:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get clinic_id from patient record
        conn_temp = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        patient_info = await conn_temp.fetchrow(
            "SELECT clinic_id FROM patients WHERE id = $1", patient_id
        )
        
        await conn_temp.close()
        
        if not patient_info:
            raise HTTPException(status_code=403, detail="Patient not found")
        
        clinic_id = patient_info['clinic_id']
        
        appointment_date = data.get("appointment_date")
        appointment_time = data.get("appointment_time")
        appointment_type = data.get("appointment_type", "CONSULTATION")
        notes = data.get("notes", "")
        
        if not appointment_date or not appointment_time:
            raise HTTPException(status_code=400, detail="Date and time required")
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Verify patient exists and get info
        patient = await conn.fetchrow("""
            SELECT id, first_name, last_name, email, clinic_id
            FROM patients
            WHERE id = $1 AND clinic_id = $2
        """, patient_id, clinic_id)
        
        if not patient:
            await conn.close()
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if slot is still available
        existing = await conn.fetchval("""
            SELECT COUNT(*) FROM appointments
            WHERE appointment_date = $1
            AND appointment_time = $2
            AND clinic_id = $3
            AND status != 'CANCELLED'
        """, appointment_date, appointment_time, clinic_id)
        
        if existing > 0:
            await conn.close()
            raise HTTPException(status_code=409, detail="Time slot no longer available")
        
        # Get a practitioner from the clinic (or let them choose)
        practitioner_id = data.get("practitioner_id")
        if not practitioner_id:
            practitioner = await conn.fetchrow("""
                SELECT id FROM users
                WHERE clinic_id = $1
                AND role IN ('clinic_admin', 'clinic_user')
                AND status = 'active'
                LIMIT 1
            """, clinic_id)
            practitioner_id = practitioner['id'] if practitioner else None
        
        # Create appointment with PENDING status (requires clinic confirmation)
        appointment = await conn.fetchrow("""
            INSERT INTO appointments (
                patient_id, clinic_id, practitioner_id,
                appointment_date, appointment_time, appointment_type,
                duration_minutes, status, notes, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, 60, 'PENDING', $7, NOW())
            RETURNING id, appointment_date, appointment_time, appointment_type
        """, patient_id, clinic_id, practitioner_id, 
            appointment_date, appointment_time, appointment_type, notes)
        
        await conn.close()
        
        # Send confirmation email
        patient_name = f"{patient['first_name']} {patient['last_name']}"
        if patient['email']:
            from datetime import datetime
            formatted_date = datetime.strptime(appointment_date, '%Y-%m-%d').strftime('%A, %d %B %Y')
            
            await email_service.send_appointment_confirmation_email(
                patient['email'],
                patient_name,
                patient_id,
                formatted_date,
                appointment_time,
                appointment_type
            )
        
        return {
            "success": True,
            "message": "Appointment request sent! Awaiting clinic confirmation.",
            "appointment": {
                "id": appointment['id'],
                "date": str(appointment['appointment_date']),
                "time": str(appointment['appointment_time']),
                "type": appointment['appointment_type'],
                "status": "PENDING"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Appointment booking error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to book appointment")


@app.delete("/api/v1/patient/appointments/{appointment_id}")
async def cancel_patient_appointment(appointment_id: int, authorization: str = Header(None)):
    """Cancel appointment - PATIENT ACCESS"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization token")
    
    try:
        # Extract patient_id from JWT token
        import jwt
        token = authorization.replace("Bearer ", "")
        
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            patient_id = int(decoded.get("sub"))
        except:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get clinic_id from patient record
        conn_temp = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        patient_info = await conn_temp.fetchrow(
            "SELECT clinic_id FROM patients WHERE id = $1", patient_id
        )
        
        await conn_temp.close()
        
        if not patient_info:
            raise HTTPException(status_code=403, detail="Patient not found")
        
        clinic_id = patient_info['clinic_id']
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Verify this appointment belongs to this patient
        appointment = await conn.fetchrow("""
            SELECT id FROM appointments
            WHERE id = $1 AND patient_id = $2 AND clinic_id = $3
        """, appointment_id, patient_id, clinic_id)
        
        if not appointment:
            await conn.close()
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Cancel appointment
        await conn.execute("""
            UPDATE appointments
            SET status = 'CANCELLED', updated_at = NOW()
            WHERE id = $1
        """, appointment_id)
        
        await conn.close()
        
        return {"success": True, "message": "Appointment cancelled"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Cancel appointment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel appointment")


# Staff confirm/decline appointment endpoints
@app.post("/api/v1/appointments/{appointment_id}/confirm")
async def confirm_appointment(appointment_id: int, authorization: str = Header(None)):
    """Confirm pending appointment - STAFF ONLY"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get appointment details
        appointment = await conn.fetchrow("""
            SELECT a.*, p.first_name, p.last_name, p.email, c.name as clinic_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN clinics c ON a.clinic_id = c.id
            WHERE a.id = $1 AND a.status = 'PENDING'
        """, appointment_id)
        
        if not appointment:
            await conn.close()
            raise HTTPException(status_code=404, detail="Appointment not found or already processed")
        
        # Update to SCHEDULED
        await conn.execute("""
            UPDATE appointments 
            SET status = 'SCHEDULED', updated_at = NOW()
            WHERE id = $1
        """, appointment_id)
        
        await conn.close()
        
        # Send confirmation email to patient
        patient_name = f"{appointment['first_name']} {appointment['last_name']}"
        if appointment['email']:
            from datetime import datetime
            formatted_date = appointment['appointment_date'].strftime('%A, %d %B %Y')
            
            await email_service.send_appointment_confirmation_email(
                appointment['email'],
                patient_name,
                appointment['patient_id'],
                formatted_date,
                str(appointment['appointment_time']),
                appointment['appointment_type']
            )
        
        return {
            "success": True,
            "message": "Appointment confirmed and patient notified"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Confirm appointment error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to confirm appointment")


@app.post("/api/v1/appointments/{appointment_id}/decline")
async def decline_appointment(appointment_id: int, data: dict, authorization: str = Header(None)):
    """Decline pending appointment - STAFF ONLY"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    try:
        reason = data.get("reason", "No reason provided")
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get appointment details
        appointment = await conn.fetchrow("""
            SELECT a.*, p.first_name, p.last_name, p.email
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.id = $1 AND a.status = 'PENDING'
        """, appointment_id)
        
        if not appointment:
            await conn.close()
            raise HTTPException(status_code=404, detail="Appointment not found or already processed")
        
        # Update to CANCELLED
        await conn.execute("""
            UPDATE appointments 
            SET status = 'CANCELLED', notes = COALESCE(notes, '') || ' [Declined: ' || $2 || ']', updated_at = NOW()
            WHERE id = $1
        """, appointment_id, reason)
        
        await conn.close()
        
        # TODO: Send decline notification email to patient
        print(f"Appointment {appointment_id} declined. Patient: {appointment['email']}")
        
        return {
            "success": True,
            "message": "Appointment declined"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Decline appointment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to decline appointment")


# ============================================================================
# SUPER ADMIN - CLINIC MANAGEMENT
# ============================================================================

@app.get("/api/v1/superadmin/stats")
async def get_superadmin_stats(authorization: str = Header(None)):
    """Get system-wide statistics - SUPER ADMIN ONLY"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    try:
        # Verify super admin role
        # TODO: Add proper JWT validation for super admin
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get system-wide stats
        total_clinics = await conn.fetchval("SELECT COUNT(*) FROM clinics")
        active_clinics = await conn.fetchval("SELECT COUNT(*) FROM clinics WHERE status = 'active'")
        pending_clinics = await conn.fetchval("SELECT COUNT(*) FROM clinics WHERE status = 'pending'")
        total_patients = await conn.fetchval("SELECT COUNT(*) FROM patients")
        total_analyses = await conn.fetchval("SELECT COUNT(*) FROM iridology_analyses")
        total_appointments = await conn.fetchval("SELECT COUNT(*) FROM appointments")
        
        await conn.close()
        
        return {
            "success": True,
            "stats": {
                "total_clinics": total_clinics,
                "active_clinics": active_clinics,
                "pending_clinics": pending_clinics,
                "total_patients": total_patients,
                "total_analyses": total_analyses,
                "total_appointments": total_appointments
            }
        }
    except Exception as e:
        print(f"Super admin stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get stats")


@app.get("/api/v1/superadmin/clinics")
async def get_all_clinics(authorization: str = Header(None)):
    """Get all clinics - SUPER ADMIN ONLY"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        clinics = await conn.fetch("""
            SELECT c.id, c.name, c.address, c.phone, c.email, c.status, c.created_at,
                   COUNT(DISTINCT p.id) as patient_count,
                   COUNT(DISTINCT u.id) as staff_count
            FROM clinics c
            LEFT JOIN patients p ON c.id = p.clinic_id
            LEFT JOIN users u ON c.id = u.clinic_id
            GROUP BY c.id, c.name, c.address, c.phone, c.email, c.status, c.created_at
            ORDER BY c.created_at DESC
        """)
        
        await conn.close()
        
        return {
            "success": True,
            "clinics": [dict(c) for c in clinics]
        }
    except Exception as e:
        print(f"Get clinics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get clinics")


@app.post("/api/v1/superadmin/clinics")
async def create_clinic(data: dict, authorization: str = Header(None)):
    """Create new clinic - SUPER ADMIN ONLY"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    try:
        clinic_name = data.get("name")
        clinic_address = data.get("address")
        clinic_phone = data.get("phone")
        clinic_email = data.get("email")
        admin_name = data.get("admin_name")
        admin_email = data.get("admin_email")
        
        if not all([clinic_name, clinic_email, admin_name, admin_email]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Check if clinic email already exists
        existing = await conn.fetchval("SELECT id FROM clinics WHERE email = $1", clinic_email)
        if existing:
            await conn.close()
            raise HTTPException(status_code=409, detail="Clinic email already exists")
        
        # Create clinic with PENDING status
        clinic = await conn.fetchrow("""
            INSERT INTO clinics (name, address, phone, email, status, created_at)
            VALUES ($1, $2, $3, $4, 'pending', NOW())
            RETURNING id, name, email
        """, clinic_name, clinic_address, clinic_phone, clinic_email)
        
        # Generate password for clinic admin
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        # Hash password
        import bcrypt
        hashed = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt(rounds=12))
        
        # Create admin user for clinic
        admin_user = await conn.fetchrow("""
            INSERT INTO users (
                clinic_id, email, password_hash, full_name, role, status, created_at
            ) VALUES ($1, $2, $3, $4, 'clinic_admin', 'active', NOW())
            RETURNING id, email
        """, clinic['id'], admin_email, hashed.decode('utf-8'), admin_name)
        
        await conn.close()
        
        # Send welcome email to clinic admin
        # TODO: Create clinic welcome email template
        print(f"Clinic created: {clinic['name']}")
        print(f"Admin: {admin_email} / Password: {temp_password}")
        
        return {
            "success": True,
            "message": "Clinic created successfully",
            "clinic": {
                "id": clinic['id'],
                "name": clinic['name'],
                "email": clinic['email'],
                "status": "pending"
            },
            "admin": {
                "email": admin_email,
                "temporary_password": temp_password
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create clinic error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to create clinic")


@app.post("/api/v1/superadmin/clinics/{clinic_id}/activate")
async def activate_clinic(clinic_id: int, authorization: str = Header(None)):
    """Activate clinic - SUPER ADMIN ONLY"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Update clinic status
        await conn.execute("""
            UPDATE clinics 
            SET status = 'active', updated_at = NOW()
            WHERE id = $1
        """, clinic_id)
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Clinic activated successfully"
        }
    except Exception as e:
        print(f"Activate clinic error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to activate clinic")


@app.post("/api/v1/superadmin/clinics/{clinic_id}/deactivate")
async def deactivate_clinic(clinic_id: int, authorization: str = Header(None)):
    """Deactivate clinic - SUPER ADMIN ONLY"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Update clinic status
        await conn.execute("""
            UPDATE clinics 
            SET status = 'inactive', updated_at = NOW()
            WHERE id = $1
        """, clinic_id)
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Clinic deactivated successfully"
        }
    except Exception as e:
        print(f"Deactivate clinic error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to deactivate clinic")


@app.delete("/api/v1/superadmin/clinics/{clinic_id}")
async def delete_clinic(clinic_id: int, authorization: str = Header(None)):
    """Delete clinic - SUPER ADMIN ONLY (use with caution)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        
        # Check if clinic has data
        patient_count = await conn.fetchval("SELECT COUNT(*) FROM patients WHERE clinic_id = $1", clinic_id)
        
        if patient_count > 0:
            await conn.close()
            raise HTTPException(status_code=400, detail=f"Cannot delete clinic with {patient_count} patients. Deactivate instead.")
        
        # Delete clinic (cascade will handle related data)
        await conn.execute("DELETE FROM clinics WHERE id = $1", clinic_id)
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Clinic deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete clinic error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete clinic")



@app.get("/api/v1/me")
async def get_current_user(authorization: str = Header(None)):
    """Get current user information from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    try:
        token = authorization.replace("Bearer ", "")
        
        # Use verify_token to decode JWT properly
        token_data = verify_token(token)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user_id = token_data.get('user_id')
        clinic_id = token_data.get('clinic_id')
        
        if not user_id:
            return {"role": "clinic_user", "clinic_id": clinic_id}
        
        # Get full user info from database
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        user = await conn.fetchrow(
            "SELECT id, email, full_name, role, clinic_id FROM users WHERE id = $1",
            user_id
        )
        await conn.close()
        
        if user:
            return {
                "id": user['id'],
                "user_id": user['id'],
                "email": user['email'],
                "full_name": user['full_name'],
                "role": user['role'],
                "clinic_id": user['clinic_id']
            }
        
        return {"id": user_id, "user_id": user_id, "clinic_id": clinic_id, "role": "clinic_user"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get user error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# ============================================================================
# SUPER ADMIN ROUTES
# ============================================================================
try:
    from super_admin_endpoints import router as super_admin_router
    app.include_router(super_admin_router)
    print("✅ Super Admin routes loaded successfully")
except Exception as e:
    print(f"⚠️  Super Admin routes not loaded: {e}")



# ============================================
# ENHANCED CLINIC DASHBOARD API ENDPOINT
# Added: 2025-11-26
# ============================================

@app.get("/api/v1/clinic/dashboard")
async def get_clinic_dashboard(current_user: dict = Depends(get_current_user)):
    """Get comprehensive dashboard data for clinic admin"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        clinic_id = current_user.get('clinic_id', 1)
        
        # Get clinic info
        clinic = await conn.fetchrow("""
            SELECT id, name, clinic_name, clinic_code, city, postcode,
                   subscription_tier, subscription_status, max_patients, max_staff,
                   features_enabled, phone, email
            FROM clinics WHERE id = $1
        """, clinic_id)
        
        # Get user info
        user = await conn.fetchrow("""
            SELECT id, full_name, email, role FROM users WHERE id = $1
        """, current_user.get('id'))
        
        # Get patient counts
        total_patients = await conn.fetchval(
            "SELECT COUNT(*) FROM patients WHERE clinic_id = $1", clinic_id
        ) or 0
        
        active_patients = await conn.fetchval(
            "SELECT COUNT(*) FROM patients WHERE clinic_id = $1 AND status = 'active'", clinic_id
        ) or 0
        
        new_patients_month = await conn.fetchval("""
            SELECT COUNT(*) FROM patients 
            WHERE clinic_id = $1 AND created_at >= date_trunc('month', CURRENT_DATE)
        """, clinic_id) or 0
        
        # Get staff count
        total_staff = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE clinic_id = $1", clinic_id
        ) or 0
        
        # Get today's appointments
        today_appointments = await conn.fetchval("""
            SELECT COUNT(*) FROM appointments 
            WHERE clinic_id = $1 AND appointment_date = CURRENT_DATE
        """, clinic_id) or 0
        
        # Get upcoming appointments (next 7 days)
        upcoming_appointments = await conn.fetchval("""
            SELECT COUNT(*) FROM appointments 
            WHERE clinic_id = $1 
            AND appointment_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
        """, clinic_id) or 0
        
        # Get today's appointment details
        today_appointment_list = await conn.fetch("""
            SELECT a.id, a.appointment_time, a.appointment_type, a.status,
                   p.first_name, p.last_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.clinic_id = $1 AND a.appointment_date = CURRENT_DATE
            ORDER BY a.appointment_time
        """, clinic_id)
        
        # Get assessment counts (from patient_assessments table)
        total_assessments = await conn.fetchval("""
            SELECT COUNT(*) FROM patient_assessments pa
            JOIN patients p ON pa.patient_id = p.id
            WHERE p.clinic_id = $1
        """, clinic_id) or 0

        pending_assessments = await conn.fetchval("""
            SELECT COUNT(*) FROM patient_assessments pa
            JOIN patients p ON pa.patient_id = p.id
            WHERE p.clinic_id = $1 AND pa.status = 'in_progress'
        """, clinic_id) or 0

        completed_assessments = await conn.fetchval("""
            SELECT COUNT(*) FROM patient_assessments pa
            JOIN patients p ON pa.patient_id = p.id
            WHERE p.clinic_id = $1 AND pa.status = 'completed'
        """, clinic_id) or 0
        
        # Get iridology counts
        total_iridology = await conn.fetchval(
            "SELECT COUNT(*) FROM iridology_analyses WHERE clinic_id = $1", clinic_id
        ) or 0
        
        completed_iridology = await conn.fetchval("""
            SELECT COUNT(*) FROM iridology_analyses
            WHERE clinic_id = $1 AND status = 'completed'
        """, clinic_id) or 0
        
        # Get invoice stats
        outstanding_invoices = await conn.fetchrow("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total
            FROM patient_invoices 
            WHERE clinic_id = $1 AND status IN ('pending', 'overdue')
        """, clinic_id)
        
        overdue_invoices = await conn.fetchval("""
            SELECT COUNT(*) FROM patient_invoices 
            WHERE clinic_id = $1 AND status = 'overdue'
        """, clinic_id) or 0
        
        revenue_this_month = await conn.fetchval("""
            SELECT COALESCE(SUM(amount), 0) FROM patient_invoices 
            WHERE clinic_id = $1 AND status = 'paid' 
            AND paid_at >= date_trunc('month', CURRENT_DATE)
        """, clinic_id) or 0
        
        # Get recent activity
        recent_patients = await conn.fetch("""
            SELECT id, first_name, last_name, created_at
            FROM patients WHERE clinic_id = $1
            ORDER BY created_at DESC LIMIT 5
        """, clinic_id)
        
        recent_assessments = await conn.fetch("""
            SELECT pa.id, pa.status, pa.created_at, p.first_name, p.last_name
            FROM patient_assessments pa
            JOIN patients p ON pa.patient_id = p.id
            WHERE p.clinic_id = $1
            ORDER BY pa.created_at DESC LIMIT 5
        """, clinic_id)
        
        recent_iridology = await conn.fetch("""
            SELECT i.id, i.status, i.created_at, p.first_name, p.last_name
            FROM iridology_analyses i
            JOIN patients p ON i.patient_id = p.id
            WHERE i.clinic_id = $1
            ORDER BY i.created_at DESC LIMIT 5
        """, clinic_id)
        
        await conn.close()
        
        # Build response
        clinic_display_name = clinic['clinic_name'] or clinic['name'] if clinic else 'Clinic'
        
        return {
            "clinic": {
                "id": clinic['id'] if clinic else clinic_id,
                "name": clinic_display_name,
                "code": clinic['clinic_code'] if clinic else '',
                "city": clinic['city'] if clinic else '',
                "subscription_tier": clinic['subscription_tier'] if clinic else 'basic',
                "subscription_status": clinic['subscription_status'] if clinic else 'active',
                "max_patients": clinic['max_patients'] if clinic else 100,
                "max_staff": clinic['max_staff'] if clinic else 5,
                "phone": clinic['phone'] if clinic else '',
                "email": clinic['email'] if clinic else ''
            },
            "user": {
                "id": user['id'] if user else current_user.get('id'),
                "full_name": user['full_name'] if user else 'User',
                "email": user['email'] if user else '',
                "role": user['role'] if user else 'staff'
            },
            "stats": {
                "total_patients": total_patients,
                "active_patients": active_patients,
                "new_patients_month": new_patients_month,
                "total_staff": total_staff,
                "today_appointments": today_appointments,
                "upcoming_appointments": upcoming_appointments,
                "total_assessments": total_assessments,
                "pending_assessments": pending_assessments,
                "completed_assessments": completed_assessments,
                "total_iridology": total_iridology,
                "completed_iridology": completed_iridology,
                "outstanding_invoices_count": outstanding_invoices['count'] if outstanding_invoices else 0,
                "outstanding_invoices_total": float(outstanding_invoices['total']) if outstanding_invoices else 0,
                "overdue_invoices": overdue_invoices,
                "revenue_this_month": float(revenue_this_month)
            },
            "today_schedule": [
                {
                    "id": apt['id'],
                    "time": str(apt['appointment_time'])[:5],
                    "patient": f"{apt['first_name']} {apt['last_name']}",
                    "type": apt['appointment_type'],
                    "status": apt['status']
                } for apt in today_appointment_list
            ],
            "recent_activity": {
                "patients": [
                    {
                        "id": p['id'],
                        "name": f"{p['first_name']} {p['last_name']}",
                        "created_at": p['created_at'].isoformat() if p['created_at'] else None
                    } for p in recent_patients
                ],
                "assessments": [
                    {
                        "id": a['id'],
                        "patient": f"{a['first_name']} {a['last_name']}",
                        "status": a['status'],
                        "created_at": a['created_at'].isoformat() if a['created_at'] else None
                    } for a in recent_assessments
                ],
                "iridology": [
                    {
                        "id": i['id'],
                        "patient": f"{i['first_name']} {i['last_name']}",
                        "status": i['status'],
                        "created_at": i['created_at'].isoformat() if i['created_at'] else None
                    } for i in recent_iridology
                ]
            },
            "alerts": {
                "overdue_invoices": overdue_invoices,
                "pending_assessments": pending_assessments,
                "follow_ups_needed": 0
            }
        }
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {str(e)}")



# ============================================
# THERAPY ASSIGNMENTS API - Added 30/11/2025
# ============================================

@app.get("/api/v1/patients/{patient_id}/therapy-assignments")
async def get_patient_therapy_assignments(patient_id: int, current_user: dict = Depends(get_current_user)):
    """Get all therapy assignments for a patient"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        clinic_id = current_user.get('clinic_id', 1)
        
        # Get therapy plan items for this patient with session counts
        assignments = await conn.fetch("""
            SELECT 
                tpi.id as assignment_id,
                tpi.therapy_code,
                tpi.therapy_name,
                tpi.recommended_sessions as total_sessions,
                tpi.session_duration_minutes,
                tp.id as plan_id,
                tp.plan_number,
                tp.status as plan_status,
                tp.created_at,
                t.applicator_placement,
                t.target_organs,
                diagram_image,
                (SELECT COUNT(*) FROM therapy_sessions ts 
                 WHERE ts.therapy_plan_item_id = tpi.id AND ts.status = 'COMPLETED') as completed_sessions
            FROM therapy_plan_items tpi
            JOIN therapy_plans tp ON tpi.therapy_plan_id = tp.id
            LEFT JOIN therapies t ON tpi.therapy_code = t.therapy_code
            WHERE tp.patient_id = $1 AND tp.clinic_id = $2
            ORDER BY tp.created_at DESC
        """, patient_id, clinic_id)
        
        await conn.close()
        
        return {
            "success": True,
            "assignments": [
                {
                    "assignment_id": a['assignment_id'],
                    "therapy_code": a['therapy_code'],
                    "therapy_name": a['therapy_name'],
                    "total_sessions": a['total_sessions'],
                    "completed_sessions": a['completed_sessions'] or 0,
                    "session_duration_minutes": a['session_duration_minutes'],
                    "plan_id": a['plan_id'],
                    "plan_number": a['plan_number'],
                    "plan_status": a['plan_status'],
                    "applicator_placement": a['applicator_placement'],
                    "target_organs": a['target_organs'],
                    "created_at": a['created_at'].isoformat() if a['created_at'] else None
                } for a in assignments
            ]
        }
    except Exception as e:
        print(f"❌ ERROR getting therapy assignments: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/patients/{patient_id}/therapy-assignments")
async def create_therapy_assignment(patient_id: int, assignment_data: dict, current_user: dict = Depends(get_current_user)):
    """Create a new therapy assignment for a patient"""
    try:
        from datetime import datetime, timedelta, time
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        clinic_id = current_user.get('clinic_id', 1)
        user_id = current_user.get('id', 1)
        
        # Extract data from request
        therapy_code = assignment_data.get('therapy_code')
        num_sessions = int(assignment_data.get('num_sessions', 16))
        session_duration = int(assignment_data.get('session_duration', 30))
        frequency = assignment_data.get('frequency', '5x_week')
        start_date_str = assignment_data.get('start_date')
        practitioner_notes = assignment_data.get('practitioner_notes', '')
        
        # Parse start date
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        # Default session time (10:00 AM)
        session_time = time(10, 0)
        
        # Get therapy details
        therapy = await conn.fetchrow(
            "SELECT * FROM therapies WHERE therapy_code = $1",
            therapy_code
        )
        
        if not therapy:
            await conn.close()
            raise HTTPException(status_code=404, detail=f"Therapy {therapy_code} not found")
        
        # Generate plan number
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        plan_number = f"TP-{timestamp}"
        
        # Create therapy plan
        plan_id = await conn.fetchval("""
            INSERT INTO therapy_plans (
                plan_number, clinic_id, patient_id, recommended_by, 
                status, notes, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
            RETURNING id
        """, plan_number, clinic_id, patient_id, user_id, 'APPROVED', practitioner_notes)
        
        # Create therapy plan item
        plan_item_id = await conn.fetchval("""
            INSERT INTO therapy_plan_items (
                therapy_plan_id, therapy_code, therapy_name, therapy_description,
                recommended_sessions, session_duration_minutes, rationale,
                target_domain, priority, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
            RETURNING id
        """, 
            plan_id,
            therapy['therapy_code'],
            therapy['therapy_name'],
            therapy['description'],
            num_sessions,
            session_duration,
            practitioner_notes,
            'ENERGY_VITALITY',
            'PRIMARY'
        )
        
        # Calculate day interval based on frequency
        if frequency == 'daily':
            day_interval = 1
            skip_weekends = False
        elif frequency == '5x_week':
            day_interval = 1
            skip_weekends = True
        elif frequency == '4x_week':
            day_interval = 2
            skip_weekends = True
        elif frequency == '3x_week':
            day_interval = 2
            skip_weekends = True
        elif frequency == '2x_week':
            day_interval = 3
            skip_weekends = True
        elif frequency == '1x_week':
            day_interval = 7
            skip_weekends = False
        elif frequency == '1x_month':
            day_interval = 30
            skip_weekends = False
        else:
            day_interval = 1
            skip_weekends = True
        
        # Create individual sessions
        sessions_created = 0
        current_date = start_date
        
        for i in range(num_sessions):
            # Skip weekends if needed
            if skip_weekends:
                while current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                    current_date += timedelta(days=1)
            
            session_number = f"TS-{plan_item_id}-{str(i+1).zfill(3)}"
            
            await conn.execute("""
                INSERT INTO therapy_sessions (
                    session_number, therapy_plan_item_id, clinic_id, patient_id,
                    session_sequence, total_sessions, scheduled_date, scheduled_time,
                    duration_minutes, status, created_at, created_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), $11)
            """,
                session_number,
                plan_item_id,
                clinic_id,
                patient_id,
                i + 1,
                num_sessions,
                current_date,
                session_time,
                session_duration,
                'SCHEDULED',
                user_id
            )
            
            sessions_created += 1
            current_date += timedelta(days=day_interval)
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Therapy assigned successfully",
            "assignment": {
                "plan_id": plan_id,
                "plan_item_id": plan_item_id,
                "plan_number": plan_number,
                "therapy_code": therapy_code,
                "therapy_name": therapy['therapy_name'],
                "sessions_created": sessions_created,
                "frequency": frequency,
                "session_duration": session_duration
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR creating therapy assignment: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/therapy-assignments/{assignment_id}/sessions")
async def get_therapy_sessions(assignment_id: int, current_user: dict = Depends(get_current_user)):
    """Get all sessions for a therapy assignment"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        sessions = await conn.fetch("""
            SELECT 
                ts.id,
                ts.session_number,
                ts.session_sequence,
                ts.total_sessions,
                ts.scheduled_date,
                ts.scheduled_time,
                ts.duration_minutes,
                ts.status,
                ts.completed_at,
                ts.therapist_notes,
                ts.patient_feedback,
                u.full_name as therapist_name
            FROM therapy_sessions ts
            LEFT JOIN users u ON ts.therapist_id = u.id
            WHERE ts.therapy_plan_item_id = $1
            ORDER BY ts.session_sequence
        """, assignment_id)
        
        await conn.close()
        
        return {
            "success": True,
            "sessions": [
                {
                    "id": s['id'],
                    "session_number": s['session_number'],
                    "session_sequence": s['session_sequence'],
                    "total_sessions": s['total_sessions'],
                    "scheduled_date": s['scheduled_date'].isoformat() if s['scheduled_date'] else None,
                    "scheduled_time": str(s['scheduled_time'])[:5] if s['scheduled_time'] else None,
                    "duration_minutes": s['duration_minutes'],
                    "status": s['status'],
                    "completed_at": s['completed_at'].isoformat() if s['completed_at'] else None,
                    "therapist_notes": s['therapist_notes'],
                    "patient_feedback": s['patient_feedback'],
                    "therapist_name": s['therapist_name']
                } for s in sessions
            ]
        }
    except Exception as e:
        print(f"❌ ERROR getting therapy sessions: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/therapy-sessions/{session_id}/complete")
async def complete_therapy_session(session_id: int, completion_data: dict = None, current_user: dict = Depends(get_current_user)):
    """Mark a therapy session as completed"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        user_id = current_user.get('id', 1)
        notes = completion_data.get('notes', '') if completion_data else ''
        feedback = completion_data.get('patient_feedback', '') if completion_data else ''
        
        await conn.execute("""
            UPDATE therapy_sessions
            SET status = 'COMPLETED',
                completed_at = NOW(),
                therapist_id = $1,
                therapist_notes = $2,
                patient_feedback = $3,
                updated_at = NOW()
            WHERE id = $4
        """, user_id, notes, feedback, session_id)
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Session marked as completed"
        }
    except Exception as e:
        print(f"❌ ERROR completing session: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/therapies/stats")
async def get_therapies_stats(current_user: dict = Depends(get_current_user)):
    """Get therapy statistics for the dashboard"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        clinic_id = current_user.get('clinic_id', 1)
        
        # Active plans count
        active_plans = await conn.fetchval("""
            SELECT COUNT(DISTINCT tp.id) 
            FROM therapy_plans tp
            WHERE tp.clinic_id = $1 AND tp.status IN ('APPROVED', 'IN_PROGRESS', 'PENDING_APPROVAL')
        """, clinic_id) or 0
        
        # Completed today
        completed_today = await conn.fetchval("""
            SELECT COUNT(*) FROM therapy_sessions
            WHERE clinic_id = $1 
            AND status = 'COMPLETED'
            AND DATE(completed_at) = CURRENT_DATE
        """, clinic_id) or 0
        
        # Today's sessions
        today_sessions = await conn.fetchval("""
            SELECT COUNT(*) FROM therapy_sessions
            WHERE clinic_id = $1 
            AND scheduled_date = CURRENT_DATE
        """, clinic_id) or 0
        
        # This week's sessions
        week_sessions = await conn.fetchval("""
            SELECT COUNT(*) FROM therapy_sessions
            WHERE clinic_id = $1 
            AND scheduled_date >= CURRENT_DATE 
            AND scheduled_date < CURRENT_DATE + INTERVAL '7 days'
        """, clinic_id) or 0
        
        await conn.close()
        
        return {
            "success": True,
            "stats": {
                "active_plans": active_plans,
                "completed_today": completed_today,
                "today_sessions": today_sessions,
                "week_sessions": week_sessions
            }
        }
    except Exception as e:
        print(f"❌ ERROR getting therapy stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/therapy-module/stats")
async def get_therapy_module_stats(current_user: dict = Depends(get_current_user)):
    """Alias for therapy stats - redirects to main stats endpoint"""
    return await get_therapies_stats(current_user)



# ============================================
# THERAPIES LIST ENDPOINT - Added 30/11/2025
# ============================================

@app.get("/api/v1/therapies")
async def get_therapies_list(current_user: dict = Depends(get_current_user)):
    """Get all available therapies"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        therapies = await conn.fetch("""
            SELECT
                id,
                therapy_code,
                therapy_name,
                subtitle,
                description,
                recommended_sessions,
                session_frequency,
                session_duration,
                applicator_placement,
                target_organs,
                is_active,
                diagram_image
            FROM therapies
            WHERE is_active = true
            ORDER BY therapy_code
        """)
        
        await conn.close()
        
        return {
            "success": True,
            "therapies": [
                {
                    "id": t['id'],
                    "therapy_code": t['therapy_code'],
                    "therapy_name": t['therapy_name'],
                    "subtitle": t['subtitle'],
                    "description": t['description'],
                    "recommended_sessions": t['recommended_sessions'],
                    "session_frequency": t['session_frequency'],
                    "session_duration": t['session_duration'],
                    "applicator_placement": t['applicator_placement'],
                    "target_organs": t['target_organs'],
                    "is_active": t['is_active'],
                    "diagram_image": t['diagram_image']
                } for t in therapies
            ]
        }
    except Exception as e:
        print(f"❌ ERROR getting therapies list: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================================
# COMPREHENSIVE THERAPIES MODULE - REBUILT 30/11/2025
# ============================================================================

@app.get("/api/v1/therapies/active-plans")
async def get_active_therapy_plans(current_user: dict = Depends(get_current_user)):
    """Get all active therapy plans with patient details and progress"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        clinic_id = current_user.get('clinic_id', 1)
        
        # Get all active therapy plans with patient info
        plans = await conn.fetch("""
            SELECT 
                tp.id as plan_id,
                tp.plan_number,
                tp.status as plan_status,
                tp.created_at,
                p.id as patient_id,
                p.patient_number,
                p.first_name,
                p.last_name
            FROM therapy_plans tp
            JOIN patients p ON tp.patient_id = p.id
            WHERE tp.clinic_id = $1 
            AND tp.status IN ('APPROVED', 'IN_PROGRESS', 'PENDING_APPROVAL')
            ORDER BY tp.created_at DESC
        """, clinic_id)
        
        result = []
        for plan in plans:
            # Get therapy items for this plan with session counts
            items = await conn.fetch("""
                SELECT 
                    tpi.id as item_id,
                    tpi.therapy_code,
                    tpi.therapy_name,
                    tpi.recommended_sessions,
                    tpi.session_duration_minutes,
                    t.target_organs,
                diagram_image,
                    t.applicator_placement,
                    t.session_frequency,
                    (SELECT COUNT(*) FROM therapy_sessions ts 
                     WHERE ts.therapy_plan_item_id = tpi.id) as total_sessions,
                    (SELECT COUNT(*) FROM therapy_sessions ts 
                     WHERE ts.therapy_plan_item_id = tpi.id AND ts.status = 'COMPLETED') as completed_sessions,
                    (SELECT scheduled_date FROM therapy_sessions ts 
                     WHERE ts.therapy_plan_item_id = tpi.id AND ts.status = 'SCHEDULED' 
                     ORDER BY scheduled_date LIMIT 1) as next_session_date,
                    (SELECT scheduled_time FROM therapy_sessions ts 
                     WHERE ts.therapy_plan_item_id = tpi.id AND ts.status = 'SCHEDULED' 
                     ORDER BY scheduled_date LIMIT 1) as next_session_time
                FROM therapy_plan_items tpi
                LEFT JOIN therapies t ON tpi.therapy_code = t.therapy_code
                WHERE tpi.therapy_plan_id = $1
            """, plan['plan_id'])
            
            therapies = []
            for item in items:
                total = item['total_sessions'] or item['recommended_sessions']
                completed = item['completed_sessions'] or 0
                progress = round((completed / total * 100) if total > 0 else 0)
                
                therapies.append({
                    "item_id": item['item_id'],
                    "therapy_code": item['therapy_code'],
                    "therapy_name": item['therapy_name'],
                    "total_sessions": total,
                    "completed_sessions": completed,
                    "progress_percent": progress,
                    "session_duration_minutes": item['session_duration_minutes'],
                    "session_frequency": item['session_frequency'],
                    "target_organs": item['target_organs'],
                    "applicator_placement": item['applicator_placement'],
                    "next_session_date": item['next_session_date'].isoformat() if item['next_session_date'] else None,
                    "next_session_time": str(item['next_session_time'])[:5] if item['next_session_time'] else None
                })
            
            if therapies:  # Only include plans that have therapy items
                result.append({
                    "plan_id": plan['plan_id'],
                    "plan_number": plan['plan_number'],
                    "plan_status": plan['plan_status'],
                    "created_at": plan['created_at'].isoformat() if plan['created_at'] else None,
                    "patient": {
                        "id": plan['patient_id'],
                        "patient_number": plan['patient_number'],
                        "first_name": plan['first_name'],
                        "last_name": plan['last_name'],
                        "initials": (plan['first_name'][0] + plan['last_name'][0]).upper() if plan['first_name'] and plan['last_name'] else "??"
                    },
                    "therapies": therapies
                })
        
        await conn.close()
        
        return {
            "success": True,
            "plans": result,
            "count": len(result)
        }
    except Exception as e:
        print(f"❌ ERROR getting active plans: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/therapies/today-sessions")
async def get_today_therapy_sessions(current_user: dict = Depends(get_current_user)):
    """Get all therapy sessions scheduled for today"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        clinic_id = current_user.get('clinic_id', 1)
        
        sessions = await conn.fetch("""
            SELECT 
                ts.id,
                ts.session_number,
                ts.session_sequence,
                ts.total_sessions,
                ts.scheduled_date,
                ts.scheduled_time,
                ts.duration_minutes,
                ts.status,
                ts.completed_at,
                tpi.therapy_code,
                tpi.therapy_name,
                p.id as patient_id,
                p.patient_number,
                p.first_name,
                p.last_name
            FROM therapy_sessions ts
            JOIN therapy_plan_items tpi ON ts.therapy_plan_item_id = tpi.id
            JOIN patients p ON ts.patient_id = p.id
            WHERE ts.clinic_id = $1 
            AND ts.scheduled_date = CURRENT_DATE
            ORDER BY ts.scheduled_time
        """, clinic_id)
        
        await conn.close()
        
        return {
            "success": True,
            "sessions": [
                {
                    "id": s['id'],
                    "session_number": s['session_number'],
                    "session_sequence": s['session_sequence'],
                    "total_sessions": s['total_sessions'],
                    "scheduled_time": str(s['scheduled_time'])[:5] if s['scheduled_time'] else None,
                    "duration_minutes": s['duration_minutes'],
                    "status": s['status'],
                    "therapy_code": s['therapy_code'],
                    "therapy_name": s['therapy_name'],
                    "patient": {
                        "id": s['patient_id'],
                        "patient_number": s['patient_number'],
                        "first_name": s['first_name'],
                        "last_name": s['last_name']
                    }
                } for s in sessions
            ],
            "count": len(sessions)
        }
    except Exception as e:
        print(f"❌ ERROR getting today sessions: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/therapy-items/{item_id}/sessions")
async def get_therapy_item_sessions(item_id: int, current_user: dict = Depends(get_current_user)):
    """Get all sessions for a specific therapy plan item"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get therapy item details
        item = await conn.fetchrow("""
            SELECT 
                tpi.id,
                tpi.therapy_code,
                tpi.therapy_name,
                tpi.recommended_sessions,
                tpi.session_duration_minutes,
                t.target_organs,
                diagram_image,
                t.applicator_placement,
                t.session_frequency,
                t.description,
                tp.patient_id,
                p.first_name,
                p.last_name,
                p.patient_number
            FROM therapy_plan_items tpi
            JOIN therapy_plans tp ON tpi.therapy_plan_id = tp.id
            JOIN patients p ON tp.patient_id = p.id
            LEFT JOIN therapies t ON tpi.therapy_code = t.therapy_code
            WHERE tpi.id = $1
        """, item_id)
        
        if not item:
            await conn.close()
            raise HTTPException(status_code=404, detail="Therapy item not found")
        
        # Get all sessions
        sessions = await conn.fetch("""
            SELECT 
                ts.id,
                ts.session_number,
                ts.session_sequence,
                ts.total_sessions,
                ts.scheduled_date,
                ts.scheduled_time,
                ts.duration_minutes,
                ts.status,
                ts.completed_at,
                ts.therapist_notes,
                ts.patient_feedback,
                u.full_name as therapist_name
            FROM therapy_sessions ts
            LEFT JOIN users u ON ts.therapist_id = u.id
            WHERE ts.therapy_plan_item_id = $1
            ORDER BY ts.session_sequence
        """, item_id)
        
        await conn.close()
        
        completed = sum(1 for s in sessions if s['status'] == 'COMPLETED')
        total = len(sessions)
        progress = round((completed / total * 100) if total > 0 else 0)
        
        return {
            "success": True,
            "therapy": {
                "item_id": item['id'],
                "therapy_code": item['therapy_code'],
                "therapy_name": item['therapy_name'],
                "description": item['description'],
                "target_organs": item['target_organs'],
                "applicator_placement": item['applicator_placement'],
                "session_frequency": item['session_frequency'],
                "session_duration_minutes": item['session_duration_minutes']
            },
            "patient": {
                "id": item['patient_id'],
                "first_name": item['first_name'],
                "last_name": item['last_name'],
                "patient_number": item['patient_number']
            },
            "progress": {
                "completed": completed,
                "total": total,
                "percent": progress
            },
            "sessions": [
                {
                    "id": s['id'],
                    "session_number": s['session_number'],
                    "session_sequence": s['session_sequence'],
                    "scheduled_date": s['scheduled_date'].isoformat() if s['scheduled_date'] else None,
                    "scheduled_time": str(s['scheduled_time'])[:5] if s['scheduled_time'] else None,
                    "duration_minutes": s['duration_minutes'],
                    "status": s['status'],
                    "completed_at": s['completed_at'].isoformat() if s['completed_at'] else None,
                    "therapist_notes": s['therapist_notes'],
                    "patient_feedback": s['patient_feedback'],
                    "therapist_name": s['therapist_name']
                } for s in sessions
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR getting therapy sessions: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/therapy-sessions/{session_id}/complete")
async def complete_therapy_session_v2(session_id: int, data: dict = None, current_user: dict = Depends(get_current_user)):
    """Mark a therapy session as completed"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        user_id = current_user.get('id', 1)
        notes = data.get('notes', '') if data else ''
        feedback = data.get('patient_feedback', '') if data else ''
        
        # Update the session
        await conn.execute("""
            UPDATE therapy_sessions
            SET status = 'COMPLETED',
                completed_at = NOW(),
                therapist_id = $1,
                therapist_notes = $2,
                patient_feedback = $3,
                updated_at = NOW()
            WHERE id = $4
        """, user_id, notes, feedback, session_id)
        
        # Get session info for appointment update
        session = await conn.fetchrow("""
            SELECT ts.*, tpi.therapy_code, tpi.therapy_name
            FROM therapy_sessions ts
            JOIN therapy_plan_items tpi ON ts.therapy_plan_item_id = tpi.id
            WHERE ts.id = $1
        """, session_id)
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Session marked as completed",
            "session": {
                "id": session_id,
                "status": "COMPLETED",
                "completed_at": "now"
            }
        }
    except Exception as e:
        print(f"❌ ERROR completing session: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/therapy-sessions/{session_id}/reschedule")
async def reschedule_therapy_session(session_id: int, data: dict, current_user: dict = Depends(get_current_user)):
    """Reschedule a therapy session"""
    try:
        from datetime import datetime, time
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        new_date_str = data.get('new_date')
        new_time_str = data.get('new_time', '10:00')
        reason = data.get('reason', '')
        
        # Parse date and time
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        time_parts = new_time_str.split(':')
        new_time = time(int(time_parts[0]), int(time_parts[1]))
        
        # Update the session
        await conn.execute("""
            UPDATE therapy_sessions
            SET scheduled_date = $1,
                scheduled_time = $2,
                updated_at = NOW()
            WHERE id = $3
        """, new_date, new_time, session_id)
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Session rescheduled successfully",
            "session": {
                "id": session_id,
                "new_date": new_date_str,
                "new_time": new_time_str
            }
        }
    except Exception as e:
        print(f"❌ ERROR rescheduling session: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/therapies/comprehensive-stats")
async def get_comprehensive_therapy_stats(current_user: dict = Depends(get_current_user)):
    """Get comprehensive therapy statistics"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        clinic_id = current_user.get('clinic_id', 1)
        
        # Active plans count
        active_plans = await conn.fetchval("""
            SELECT COUNT(DISTINCT tp.id) 
            FROM therapy_plans tp
            WHERE tp.clinic_id = $1 AND tp.status IN ('APPROVED', 'IN_PROGRESS')
        """, clinic_id) or 0
        
        # Completed today
        completed_today = await conn.fetchval("""
            SELECT COUNT(*) FROM therapy_sessions
            WHERE clinic_id = $1 
            AND status = 'COMPLETED'
            AND DATE(completed_at) = CURRENT_DATE
        """, clinic_id) or 0
        
        # Today's sessions
        today_sessions = await conn.fetchval("""
            SELECT COUNT(*) FROM therapy_sessions
            WHERE clinic_id = $1 
            AND scheduled_date = CURRENT_DATE
        """, clinic_id) or 0
        
        # This week's sessions
        week_sessions = await conn.fetchval("""
            SELECT COUNT(*) FROM therapy_sessions
            WHERE clinic_id = $1 
            AND scheduled_date >= CURRENT_DATE 
            AND scheduled_date < CURRENT_DATE + INTERVAL '7 days'
        """, clinic_id) or 0
        
        # Patients with active therapy
        patients_with_therapy = await conn.fetchval("""
            SELECT COUNT(DISTINCT tp.patient_id)
            FROM therapy_plans tp
            WHERE tp.clinic_id = $1 AND tp.status IN ('APPROVED', 'IN_PROGRESS')
        """, clinic_id) or 0
        
        # Total sessions scheduled
        total_scheduled = await conn.fetchval("""
            SELECT COUNT(*) FROM therapy_sessions
            WHERE clinic_id = $1 AND status = 'SCHEDULED'
        """, clinic_id) or 0
        
        await conn.close()
        
        return {
            "success": True,
            "stats": {
                "active_plans": active_plans,
                "completed_today": completed_today,
                "today_sessions": today_sessions,
                "week_sessions": week_sessions,
                "patients_with_therapy": patients_with_therapy,
                "total_scheduled": total_scheduled
            }
        }
    except Exception as e:
        print(f"❌ ERROR getting therapy stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/therapy-sessions/{session_id}/create-appointment")
async def create_appointment_from_session(session_id: int, current_user: dict = Depends(get_current_user)):
    """Create an appointment from a therapy session"""
    try:
        from datetime import datetime
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        clinic_id = current_user.get('clinic_id', 1)
        user_id = current_user.get('id', 1)
        
        # Get session details
        session = await conn.fetchrow("""
            SELECT ts.*, tpi.therapy_code, tpi.therapy_name, p.first_name, p.last_name
            FROM therapy_sessions ts
            JOIN therapy_plan_items tpi ON ts.therapy_plan_item_id = tpi.id
            JOIN patients p ON ts.patient_id = p.id
            WHERE ts.id = $1
        """, session_id)
        
        if not session:
            await conn.close()
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate appointment number
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        appointment_number = f"APT-{timestamp}"
        
        # Create appointment
        appointment_id = await conn.fetchval("""
            INSERT INTO appointments (
                appointment_number, clinic_id, patient_id, appointment_type,
                appointment_date, appointment_time, duration_minutes,
                status, booking_notes, created_at, created_by
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), $10)
            RETURNING id
        """,
            appointment_number,
            clinic_id,
            session['patient_id'],
            'THERAPY_SESSION',
            session['scheduled_date'],
            session['scheduled_time'],
            session['duration_minutes'],
            'SCHEDULED',
            f"Therapy: {session['therapy_code']} - {session['therapy_name']} (Session {session['session_sequence']} of {session['total_sessions']})",
            user_id
        )
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Appointment created successfully",
            "appointment": {
                "id": appointment_id,
                "appointment_number": appointment_number,
                "date": session['scheduled_date'].isoformat(),
                "time": str(session['scheduled_time'])[:5]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR creating appointment: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/therapy-items/{item_id}/create-all-appointments")
async def create_all_appointments_for_therapy(item_id: int, current_user: dict = Depends(get_current_user)):
    """Create appointments for all scheduled sessions of a therapy"""
    try:
        from datetime import datetime
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        clinic_id = current_user.get('clinic_id', 1)
        user_id = current_user.get('id', 1)
        
        # Get therapy item details
        item = await conn.fetchrow("""
            SELECT tpi.*, tp.patient_id
            FROM therapy_plan_items tpi
            JOIN therapy_plans tp ON tpi.therapy_plan_id = tp.id
            WHERE tpi.id = $1
        """, item_id)
        
        if not item:
            await conn.close()
            raise HTTPException(status_code=404, detail="Therapy item not found")
        
        # Get all scheduled sessions
        sessions = await conn.fetch("""
            SELECT * FROM therapy_sessions
            WHERE therapy_plan_item_id = $1 AND status = 'SCHEDULED'
            ORDER BY session_sequence
        """, item_id)
        
        appointments_created = 0
        for session in sessions:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            appointment_number = f"APT-{timestamp}-{session['session_sequence']}"
            
            await conn.execute("""
                INSERT INTO appointments (
                    appointment_number, clinic_id, patient_id, appointment_type,
                    appointment_date, appointment_time, duration_minutes,
                    status, booking_notes, created_at, created_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), $10)
            """,
                appointment_number,
                clinic_id,
                item['patient_id'],
                'THERAPY_SESSION',
                session['scheduled_date'],
                session['scheduled_time'],
                session['duration_minutes'],
                'SCHEDULED',
                f"Therapy: {item['therapy_code']} - {item['therapy_name']} (Session {session['session_sequence']} of {session['total_sessions']})",
                user_id
            )
            appointments_created += 1
        
        await conn.close()
        
        return {
            "success": True,
            "message": f"{appointments_created} appointments created successfully",
            "appointments_created": appointments_created
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR creating appointments: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



# ============================================
# THERAPY DIAGRAM UPLOAD - Added 30/11/2025
# ============================================

from fastapi import File, UploadFile
import base64
import os

@app.post("/api/v1/therapies/{therapy_code}/upload-diagram")
async def upload_therapy_diagram(therapy_code: str, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload a diagram image for a therapy"""
    try:
        # Validate file type
        allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PNG, JPEG, GIF, WEBP allowed.")
        
        # Read file content
        content = await file.read()
        
        # Generate filename
        import uuid
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'
        filename = f"{therapy_code}_{uuid.uuid4().hex[:8]}.{ext}"
        
        # Save to uploads directory
        upload_dir = "/var/www/Celloxen-C1000/frontend/uploads/therapy_diagrams"
        filepath = os.path.join(upload_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        # Update database with image path
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        image_url = f"/uploads/therapy_diagrams/{filename}"
        
        await conn.execute("""
            UPDATE therapies SET diagram_image = $1, updated_at = NOW()
            WHERE therapy_code = $2
        """, image_url, therapy_code)
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Diagram uploaded successfully",
            "image_url": image_url,
            "therapy_code": therapy_code
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR uploading diagram: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/therapies/{therapy_code}/diagram")
async def delete_therapy_diagram(therapy_code: str, current_user: dict = Depends(get_current_user)):
    """Delete the diagram for a therapy"""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Get current image path
        current_image = await conn.fetchval(
            "SELECT diagram_image FROM therapies WHERE therapy_code = $1",
            therapy_code
        )
        
        # Delete file if exists
        if current_image:
            filepath = f"/var/www/Celloxen-C1000/frontend{current_image}"
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Clear database
        await conn.execute("""
            UPDATE therapies SET diagram_image = NULL, updated_at = NOW()
            WHERE therapy_code = $1
        """, therapy_code)
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Diagram deleted successfully"
        }
        
    except Exception as e:
        print(f"❌ ERROR deleting diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# ============================================
# CLINIC SETTINGS ENDPOINTS - Added 30/11/2025
# ============================================

@app.get("/api/v1/clinic/settings")
async def get_clinic_settings(current_user: dict = Depends(get_current_user)):
    """Get clinic settings"""
    try:
        clinic_id = current_user.get('clinic_id')
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        clinic = await conn.fetchrow(
            "SELECT * FROM clinics WHERE id = $1", clinic_id
        )
        await conn.close()
        
        if not clinic:
            return {"success": True, "settings": {}}
        
        return {
            "success": True,
            "profile": {
                "name": clinic.get('name', '') or clinic.get('clinic_name', ''),
                "phone": clinic.get('phone', ''),
                "email": clinic.get('email', ''),
                "address_line1": clinic.get('address_line1', ''),
                "address_line2": clinic.get('address_line2', ''),
                "city": clinic.get('city', ''),
                "county": clinic.get('county', ''),
                "postcode": clinic.get('postcode', ''),
                "website": clinic.get('website', '')
            },
            "opening_hours": clinic.get('opening_hours') if isinstance(clinic.get('opening_hours'), list) else [
                {"day": 0, "is_open": False, "open_time": "09:00", "close_time": "17:00"},
                {"day": 1, "is_open": True, "open_time": "09:00", "close_time": "17:00"},
                {"day": 2, "is_open": True, "open_time": "09:00", "close_time": "17:00"},
                {"day": 3, "is_open": True, "open_time": "09:00", "close_time": "17:00"},
                {"day": 4, "is_open": True, "open_time": "09:00", "close_time": "17:00"},
                {"day": 5, "is_open": True, "open_time": "09:00", "close_time": "17:00"},
                {"day": 6, "is_open": False, "open_time": "09:00", "close_time": "17:00"}
            ],
            "notifications": clinic.get('notifications', {}) or {}
        }
    except Exception as e:
        print(f"❌ ERROR getting clinic settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/v1/clinic/settings/profile")
async def update_clinic_profile(data: dict, current_user: dict = Depends(get_current_user)):
    """Update clinic profile"""
    try:
        clinic_id = current_user.get('clinic_id')
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        await conn.execute("""
            UPDATE clinics SET
                name = COALESCE($1, name),
                phone = COALESCE($2, phone),
                address_line1 = COALESCE($3, address_line1),
                address_line2 = COALESCE($4, address_line2),
                city = COALESCE($5, city),
                county = COALESCE($6, county),
                postcode = COALESCE($7, postcode),
                website = COALESCE($8, website),
                updated_at = NOW()
            WHERE id = $9
        """, 
            data.get('clinic_name'),
            data.get('phone'),
            data.get('address_line1'),
            data.get('address_line2'),
            data.get('city'),
            data.get('county'),
            data.get('postcode'),
            data.get('website'),
            clinic_id
        )
        await conn.close()
        
        return {"success": True, "message": "Profile updated successfully"}
    except Exception as e:
        print(f"❌ ERROR updating clinic profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/v1/clinic/settings/hours")
async def update_clinic_hours(data: dict, current_user: dict = Depends(get_current_user)):
    """Update clinic opening hours"""
    try:
        clinic_id = current_user.get('clinic_id')
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        hours_list = data.get('hours', [])
        
        for hour in hours_list:
            day = hour.get('day')
            is_open = hour.get('is_open', True)
            open_time = hour.get('open_time', '09:00')
            close_time = hour.get('close_time', '17:00')
            
            # Upsert into opening_hours table
            await conn.execute("""
                INSERT INTO opening_hours (clinic_id, day_of_week, is_open, open_time, close_time, updated_at)
                VALUES ($1, $2, $3, $4::time, $5::time, NOW())
                ON CONFLICT (clinic_id, day_of_week)
                DO UPDATE SET is_open = $3, open_time = $4::time, close_time = $5::time, updated_at = NOW()
            """, clinic_id, day, is_open, open_time, close_time)
        
        await conn.close()
        
        return {"success": True, "message": "Opening hours updated successfully"}
    except Exception as e:
        print(f"❌ ERROR updating clinic hours: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/v1/clinic/settings/password")
async def update_user_password(data: dict, current_user: dict = Depends(get_current_user)):
    """Update user password"""
    try:
        user_id = current_user.get('sub') or current_user.get('user_id')
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Verify current password
        user = await conn.fetchrow("SELECT password_hash FROM users WHERE id = $1", int(user_id))
        if not user or not bcrypt.checkpw(data.get('current_password', '').encode(), user['password_hash'].encode()):
            await conn.close()
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Hash new password
        new_hash = bcrypt.hashpw(data.get('new_password', '').encode(), bcrypt.gensalt()).decode()
        
        await conn.execute(
            "UPDATE users SET password_hash = $1, updated_at = NOW() WHERE id = $2",
            new_hash, int(user_id)
        )
        await conn.close()
        
        return {"success": True, "message": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR updating password: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/v1/clinic/settings/notifications")
async def update_notification_settings(data: dict, current_user: dict = Depends(get_current_user)):
    """Update notification settings"""
    try:
        clinic_id = current_user.get('clinic_id')
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        notifications = data.get('notifications', {})
        
        await conn.execute("""
            UPDATE clinics SET
                email_appointment_reminders = COALESCE($1, email_appointment_reminders),
                email_appointment_confirmations = COALESCE($2, email_appointment_confirmations),
                email_new_patient_alerts = COALESCE($3, email_new_patient_alerts),
                email_invoice_notifications = COALESCE($4, email_invoice_notifications),
                email_marketing = COALESCE($5, email_marketing),
                updated_at = NOW()
            WHERE id = $6
        """,
            notifications.get('appointment_reminders'),
            notifications.get('appointment_confirmations'),
            notifications.get('new_patient_alerts'),
            notifications.get('invoice_notifications'),
            notifications.get('marketing'),
            clinic_id
        )
        await conn.close()
        
        return {"success": True, "message": "Notification settings updated successfully"}
    except Exception as e:
        print(f"❌ ERROR updating notifications: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PATIENT INVOICES V2 ENDPOINT - Added 30/11/2025
# ============================================

@app.get("/api/v1/clinic/patient-invoices/v2")
async def get_patient_invoices_v2(current_user: dict = Depends(get_current_user)):
    """Get all patient invoices for the clinic (v2)"""
    try:
        clinic_id = current_user.get('clinic_id')
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        invoices = await conn.fetch("""
            SELECT 
                i.id,
                i.invoice_number,
                i.patient_id,
                i.amount,
                i.description,
                i.service_date,
                i.due_date,
                i.status,
                i.created_at,
                i.paid_at,
                i.payment_date,
                i.payment_method,
                i.notes,
                p.first_name,
                p.last_name,
                p.patient_number,
                p.email as patient_email
            FROM patient_invoices i
            JOIN patients p ON i.patient_id = p.id
            WHERE i.clinic_id = $1
            ORDER BY i.created_at DESC
        """, clinic_id)
        await conn.close()
        
        return {
            "success": True,
            "invoices": [
                {
                    "id": inv['id'],
                    "invoice_number": inv['invoice_number'],
                    "patient_id": inv['patient_id'],
                    "patient_name": f"{inv['first_name']} {inv['last_name']}",
                    "patient_number": inv['patient_number'],
                    "patient_email": inv['patient_email'],
                    "amount": float(inv['amount']) if inv['amount'] else 0,
                    "status": inv['status'],
                    "service_date": inv['service_date'].isoformat() if inv.get('service_date') else None,
                    "due_date": inv['due_date'].isoformat() if inv.get('due_date') else None,
                    "paid_at": inv['paid_at'].isoformat() if inv.get('paid_at') else None,
                    "payment_date": inv['payment_date'].isoformat() if inv.get('payment_date') else None,
                    "payment_method": inv.get('payment_method', ''),
                    "description": inv.get('description', ''),
                    "notes": inv.get('notes', ''),
                    "created_at": inv['created_at'].isoformat() if inv['created_at'] else None
                } for inv in invoices
            ],
            "count": len(invoices)
        }
    except Exception as e:
        print(f"❌ ERROR getting patient invoices v2: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/v1/clinic/patient-invoices/{invoice_id}/status")
async def update_patient_invoice_status(invoice_id: int, status_data: dict, current_user: dict = Depends(get_current_user)):
    """Update patient invoice status"""
    try:
        clinic_id = current_user.get('clinic_id')
        new_status = status_data.get('status')

        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required")

        # Valid statuses for invoices
        valid_statuses = ['pending', 'paid', 'overdue', 'cancelled']
        if new_status.lower() not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )

        # Verify invoice belongs to clinic
        invoice = await conn.fetchrow(
            "SELECT id, status FROM patient_invoices WHERE id = $1 AND clinic_id = $2",
            invoice_id, clinic_id
        )

        if not invoice:
            await conn.close()
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Update status and set paid_at if marking as paid
        if new_status.lower() == 'paid':
            await conn.execute(
                "UPDATE patient_invoices SET status = $1, paid_at = NOW(), payment_date = NOW() WHERE id = $2",
                new_status.lower(), invoice_id
            )
        else:
            await conn.execute(
                "UPDATE patient_invoices SET status = $1 WHERE id = $2",
                new_status.lower(), invoice_id
            )

        await conn.close()

        return {
            "success": True,
            "message": f"Invoice status updated to {new_status}",
            "invoice_id": invoice_id,
            "new_status": new_status.lower()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR updating invoice status: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

