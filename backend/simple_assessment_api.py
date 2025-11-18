"""
SIMPLE ASSESSMENT API - Clean, Working System
Handles 35-question assessment with simple scoring
"""
from fastapi import APIRouter, HTTPException
import asyncpg
from typing import List, Dict
from pydantic import BaseModel

router = APIRouter()

# Database connection
async def get_db():
    return await asyncpg.connect(
        host="localhost",
        port=5432,
        user="celloxen_user",
        password="CelloxenSecure2025",
        database="celloxen_portal"
    )

# ==================== MODELS ====================
class AssessmentAnswer(BaseModel):
    question_id: int
    answer_index: int  # 0-4

class AssessmentSubmission(BaseModel):
    patient_id: int
    answers: List[AssessmentAnswer]

# ==================== GET ALL 35 QUESTIONS ====================
@router.get("/api/v1/assessment/questions")
async def get_assessment_questions():
    """Get all 35 wellness questions"""
    conn = await get_db()
    
    questions = await conn.fetch("""
        SELECT 
            id,
            therapy_domain,
            question_text,
            question_type,
            question_order,
            response_options
        FROM assessment_questions
        ORDER BY question_order
    """)
    
    await conn.close()
    
    return {
        "success": True,
        "total_questions": len(questions),
        "questions": [dict(q) for q in questions]
    }

# ==================== SUBMIT ASSESSMENT ====================
@router.post("/api/v1/assessment/submit")
async def submit_assessment(submission: AssessmentSubmission):
    """
    Submit completed 35-question assessment
    Calculate scores and save to database
    """
    conn = await get_db()
    
    try:
        # Get all questions to validate and calculate scores
        questions = await conn.fetch("""
            SELECT id, therapy_domain, question_order
            FROM assessment_questions
            ORDER BY question_order
        """)
        
        # Validate we have 35 answers
        if len(submission.answers) != 35:
            raise HTTPException(
                status_code=400, 
                detail=f"Expected 35 answers, got {len(submission.answers)}"
            )
        
        # Calculate domain scores
        domain_scores = {
            'C-102': [],  # Energy (Q1-7)
            'C-104': [],  # Comfort (Q8-14)
            'C-105': [],  # Circulation (Q15-21)
            'C-107': [],  # Stress (Q22-28)
            'C-108': []   # Metabolic (Q29-35)
        }
        
        # Group answers by domain
        for answer in submission.answers:
            question = next((q for q in questions if q['id'] == answer.question_id), None)
            if not question:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid question_id: {answer.question_id}"
                )
            
            # Convert answer (0-4) to percentage (0-100)
            # 0 = 0%, 1 = 25%, 2 = 50%, 3 = 75%, 4 = 100%
            score = (answer.answer_index / 4) * 100
            
            domain = question['therapy_domain']
            domain_scores[domain].append(score)
        
        # Calculate average for each domain
        energy_score = sum(domain_scores['C-102']) / len(domain_scores['C-102'])
        comfort_score = sum(domain_scores['C-104']) / len(domain_scores['C-104'])
        circulation_score = sum(domain_scores['C-105']) / len(domain_scores['C-105'])
        stress_score = sum(domain_scores['C-107']) / len(domain_scores['C-107'])
        metabolic_score = sum(domain_scores['C-108']) / len(domain_scores['C-108'])
        
        # Overall score is average of all domains
        overall_score = (energy_score + comfort_score + circulation_score + 
                        stress_score + metabolic_score) / 5
        
        # Create assessment record
        assessment = await conn.fetchrow("""
            INSERT INTO patient_assessments (
                patient_id,
                energy_score,
                comfort_score,
                circulation_score,
                stress_score,
                metabolic_score,
                overall_score,
                status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'completed')
            RETURNING id
        """, submission.patient_id, energy_score, comfort_score, 
            circulation_score, stress_score, metabolic_score, overall_score)
        
        assessment_id = assessment['id']
        
        # Save all responses
        for answer in submission.answers:
            await conn.execute("""
                INSERT INTO assessment_responses (
                    assessment_id,
                    question_id,
                    answer_index
                ) VALUES ($1, $2, $3)
            """, assessment_id, answer.question_id, answer.answer_index)
        
        await conn.close()
        
        return {
            "success": True,
            "assessment_id": assessment_id,
            "scores": {
                "energy": round(energy_score, 2),
                "comfort": round(comfort_score, 2),
                "circulation": round(circulation_score, 2),
                "stress": round(stress_score, 2),
                "metabolic": round(metabolic_score, 2),
                "overall": round(overall_score, 2)
            },
            "message": "Assessment completed successfully!"
        }
        
    except Exception as e:
        await conn.close()
        raise HTTPException(status_code=500, detail=str(e))

# ==================== GET PATIENT'S LATEST ASSESSMENT ====================
@router.get("/api/v1/assessment/patient/{patient_id}/latest")
async def get_patient_latest_assessment(patient_id: int):
    """Get patient's most recent assessment with scores"""
    conn = await get_db()
    
    assessment = await conn.fetchrow("""
        SELECT * FROM patient_assessments
        WHERE patient_id = $1
        ORDER BY created_at DESC
        LIMIT 1
    """, patient_id)
    
    await conn.close()
    
    if not assessment:
        return {
            "success": True,
            "has_assessment": False,
            "message": "No assessment found for this patient"
        }
    
    return {
        "success": True,
        "has_assessment": True,
        "assessment": {
            "id": assessment['id'],
            "date": str(assessment['assessment_date']),
            "scores": {
                "energy": float(assessment['energy_score']),
                "comfort": float(assessment['comfort_score']),
                "circulation": float(assessment['circulation_score']),
                "stress": float(assessment['stress_score']),
                "metabolic": float(assessment['metabolic_score']),
                "overall": float(assessment['overall_score'])
            },
            "status": assessment['status']
        }
    }

# ==================== PDF REPORT GENERATION ====================
from pdf_report_generator import generate_pdf_report
from fastapi.responses import Response

@router.get("/api/v1/assessment/{assessment_id}/report")
async def download_assessment_report(assessment_id: int):
    """Generate and download PDF wellness report"""
    conn = await get_db()
    
    try:
        # Get assessment
        assessment = await conn.fetchrow("""
            SELECT * FROM patient_assessments WHERE id = $1
        """, assessment_id)
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Get patient
        patient = await conn.fetchrow("""
            SELECT * FROM patients WHERE id = $1
        """, assessment['patient_id'])
        
        # Generate PDF
        pdf_bytes = generate_pdf_report(dict(patient), dict(assessment))
        
        # Return as downloadable PDF
        filename = f"wellness_report_{patient['patient_number']}_{assessment_id}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
    finally:
        await conn.close()

