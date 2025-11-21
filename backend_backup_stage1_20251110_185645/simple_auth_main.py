from fastapi import FastAPI, HTTPException
from patient_portal_endpoints import router as patient_router
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from datetime import datetime
import json

# Assessment Module Imports
from celloxen_assessment_system import (
    ASSESSMENT_QUESTIONS,
    THERAPY_PROTOCOLS,
    calculate_assessment_score,
    generate_therapy_recommendations,
    generate_multi_domain_recommendations
)

app = FastAPI()

# Include patient portal router
app.include_router(patient_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://celloxen.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/auth/login")
async def login(user_credentials: dict):
    try:
        email = user_credentials.get("email")
        password = user_credentials.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user", 
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
        
        if not user or password != "password123":
            await conn.close()
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        await conn.close()
        
        return {
            "access_token": f"token_for_{user['email']}",
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user['full_name'],
                "role": user['role'],
                "status": user['status']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/auth/me")
async def get_current_user():
    return {"id": 1, "email": "admin@celloxen.com", "role": "super_admin"}

@app.get("/api/v1/patients/stats/overview")
async def get_patient_stats():
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user", 
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        total_patients = await conn.fetchval("SELECT COUNT(*) FROM patients")
        await conn.close()
        
        return {
            "total_patients": total_patients,
            "active_patients": total_patients,
            "new_this_month": 0,
            "assessments_completed": 0
        }
    except Exception as e:
        return {"total_patients": 1, "active_patients": 1, "new_this_month": 0, "assessments_completed": 0}

@app.get("/api/v1/clinic/patients")
async def get_clinic_patients():
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user", 
            password="CelloxenSecure2025", database="celloxen_portal"
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

@app.post("/api/v1/clinic/patients")
async def create_patient(patient_data: dict):
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user", 
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        # Generate patient number
        next_number = await conn.fetchval("SELECT COUNT(*) + 1 FROM patients")
        patient_number = f"CLX-ABD-{next_number:05d}"
        
        # Convert date string to date object
        date_str = patient_data.get('date_of_birth')
        if date_str:
            birth_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            raise HTTPException(status_code=400, detail="Date of birth is required")
        
        patient_id = await conn.fetchval("""
            INSERT INTO patients (
                patient_number, clinic_id, first_name, last_name, 
                email, mobile_phone, date_of_birth, address,
                emergency_contact, emergency_phone, medical_conditions,
                medications, allergies, insurance_details, notes,
                status, portal_access, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
            RETURNING id
        """, 
        patient_number, 1,
        patient_data.get('first_name'), patient_data.get('last_name'),
        patient_data.get('email'), patient_data.get('mobile_phone'),
        birth_date, patient_data.get('address'),
        patient_data.get('emergency_contact'), patient_data.get('emergency_phone'),
        patient_data.get('medical_conditions'), patient_data.get('medications'),
        patient_data.get('allergies'), patient_data.get('insurance_details'),
        patient_data.get('notes'), 'active', True, datetime.now()
        )
        
        await conn.close()
        return {"success": True, "patient_id": patient_id, "patient_number": patient_number}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/clinic/patients/{patient_id}")
async def update_patient(patient_id: int, patient_data: dict):
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user", 
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/clinic/patients/{patient_id}")
async def delete_patient(patient_id: int):
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user", 
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        await conn.execute("DELETE FROM patients WHERE id = $1", patient_id)
        await conn.close()
        return {"success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/clinic/patients/{patient_id}")
async def get_patient(patient_id: int):
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user", 
            password="CelloxenSecure2025", database="celloxen_portal"
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
async def create_comprehensive_assessment(assessment_data: dict):
    """Create a comprehensive assessment with questionnaire and optional iridology"""
    try:
        patient_id = assessment_data.get("patient_id")
        questionnaire_responses = assessment_data.get("questionnaire_responses", {})
        iris_images = assessment_data.get("iris_images", {})
        
        if not patient_id:
            raise HTTPException(status_code=400, detail="patient_id is required")
        
        # Connect to database
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/assessments/{assessment_id}")
async def get_assessment_details(assessment_id: int):
    """Get detailed assessment results"""
    try:
        import json
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        # Get various stats
        total = await conn.fetchval("SELECT COUNT(*) FROM appointments")
        today = await conn.fetchval(
            "SELECT COUNT(*) FROM appointments WHERE appointment_date = CURRENT_DATE"
        )
        scheduled = await conn.fetchval(
            "SELECT COUNT(*) FROM appointments WHERE status = 'SCHEDULED'"
        )
        completed = await conn.fetchval(
            "SELECT COUNT(*) FROM appointments WHERE status = 'COMPLETED'"
        )
        
        await conn.close()
        
        return {
            "total_appointments": total,
            "today_appointments": today,
            "scheduled_appointments": scheduled,
            "completed_appointments": completed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/appointments")
async def get_appointments(
    status: str = None,
    date: str = None,
    patient_id: int = None
):
    """Get all appointments with optional filters"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/appointments")
async def create_appointment(appointment_data: dict):
    """Create a new appointment"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        # Generate appointment number
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        appointment_number = f"APT-{timestamp}"
        
        # Insert appointment
        from datetime import datetime, date, time
        
        # Convert date string to date object
        appt_date = datetime.strptime(appointment_data["appointment_date"], "%Y-%m-%d").date()
        # Convert time string to time object
        appt_time = datetime.strptime(appointment_data["appointment_time"], "%H:%M").time()
        
        appointment_id = await conn.fetchval(
            """INSERT INTO appointments (
                appointment_number, clinic_id, patient_id, appointment_type,
                appointment_date, appointment_time, duration_minutes,
                practitioner_id, status, booking_notes, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
            RETURNING id""",
            appointment_number,
            appointment_data.get("clinic_id", 1),
            appointment_data["patient_id"],
            appointment_data["appointment_type"],
            appt_date,
            appt_time,
            appointment_data.get("duration_minutes", 60),
            appointment_data.get("practitioner_id"),
            'SCHEDULED',
            appointment_data.get("booking_notes")
        )
        
        await conn.close()
        
        return {
            "success": True,
            "message": "Appointment created successfully",
            "appointment_id": appointment_id,
            "appointment_number": appointment_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/appointments/{appointment_id}")
async def get_appointment(appointment_id: int):
    """Get a specific appointment by ID"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/appointments/{appointment_id}")
async def update_appointment(appointment_id: int, appointment_data: dict):
    """Update an existing appointment"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        # Check if appointment exists
        exists = await conn.fetchval(
            "SELECT id FROM appointments WHERE id = $1", appointment_id
        )
        if not exists:
            await conn.close()
            raise HTTPException(status_code=404, detail="Appointment not found")
        
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
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/appointments/{appointment_id}")
async def delete_appointment(appointment_id: int):
    """Delete an appointment"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/appointments/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: int, cancel_data: dict):
    """Cancel an appointment"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/appointments/calendar/{year}/{month}")
async def get_calendar_appointments(year: int, month: int):
    """Get appointments for a specific month (calendar view)"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))




# ============================================================================
# THERAPY PLANS ENDPOINTS
# ============================================================================

@app.get("/api/v1/therapy-plans/stats")
async def get_therapy_plans_stats():
    """Get therapy plans statistics"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/therapy-plans")
async def get_therapy_plans(status: str = None, patient_id: int = None):
    """Get all therapy plans with optional filters"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/therapy-plans/{plan_id}")
async def get_therapy_plan(plan_id: int):
    """Get a specific therapy plan with items"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/therapy-plans")
async def create_therapy_plan(plan_data: dict):
    """Create a new therapy plan"""
    try:
        from datetime import datetime
        
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        # Generate plan number
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        plan_number = f"TP-{timestamp}"
        
        # Insert therapy plan
        plan_id = await conn.fetchval(
            """INSERT INTO therapy_plans (
                plan_number, clinic_id, patient_id, assessment_id,
                recommended_by, status, notes, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
            RETURNING id""",
            plan_number,
            plan_data.get("clinic_id", 1),
            plan_data["patient_id"],
            plan_data["assessment_id"],
            plan_data.get("recommended_by", 1),
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
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/therapy-plans/{plan_id}/status")
async def update_therapy_plan_status(plan_id: int, status_data: dict):
    """Update therapy plan status"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))




# ============================================================================
# REPORTS ENDPOINTS
# ============================================================================

@app.get("/api/v1/reports/overview")
async def get_reports_overview():
    """Get overall system statistics"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/reports/patient-activity")
async def get_patient_activity():
    """Get patient activity report"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/reports/wellness-trends")
async def get_wellness_trends():
    """Get wellness score trends over time"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
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
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/health")
async def health():
    return {"status": "healthy"}
