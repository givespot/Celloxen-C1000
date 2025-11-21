"""
Assessment Module API Endpoints
Add these to your simple_auth_main.py
"""

from fastapi import HTTPException, Depends
from typing import Dict, Optional
import json
from datetime import datetime

# Import the assessment system
from celloxen_assessment_system import (
    ASSESSMENT_QUESTIONS,
    THERAPY_PROTOCOLS,
    calculate_assessment_score,
    generate_therapy_recommendations,
    generate_multi_domain_recommendations
)

# ============= ASSESSMENT ENDPOINTS =============

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
            detail=f"Domain '{domain}' not found. Available domains: {list(ASSESSMENT_QUESTIONS.keys())}"
        )
    
    return {
        "success": True,
        "domain": domain,
        "domain_info": ASSESSMENT_QUESTIONS[domain],
        "total_questions": len(ASSESSMENT_QUESTIONS[domain]["questions"])
    }

@app.post("/api/v1/assessments/comprehensive")
async def create_comprehensive_assessment(
    assessment_data: dict, 
    current_user: dict = Depends(verify_token)
):
    """
    Create a comprehensive assessment with questionnaire and optional iridology
    """
    try:
        patient_id = assessment_data.get("patient_id")
        questionnaire_responses = assessment_data.get("questionnaire_responses", {})
        iris_images = assessment_data.get("iris_images", {})
        
        if not patient_id:
            raise HTTPException(status_code=400, detail="patient_id is required")
        
        # Validate patient exists and user has access
        async with get_db_connection() as conn:
            # Check if user is super admin or clinic matches
            if current_user.get("role") == "super_admin":
                patient = await conn.fetchrow(
                    "SELECT * FROM patients WHERE id = $1",
                    patient_id
                )
            else:
                patient = await conn.fetchrow(
                    """SELECT p.* FROM patients p 
                       WHERE p.id = $1 AND p.centre_id = $2""",
                    patient_id, current_user["centre_id"]
                )
            
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found or access denied")
        
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
        
        # Calculate overall wellness score (average of all domain scores)
        total_score = 0
        domain_count = 0
        for domain, score_data in questionnaire_scores.items():
            if score_data.get("score", 0) > 0:
                total_score += score_data["score"]
                domain_count += 1
        
        overall_wellness_score = round(total_score / domain_count, 2) if domain_count > 0 else 0
        
        # Determine assessment status
        has_iris_images = iris_images.get('left') and iris_images.get('right')
        assessment_status = 'completed' if has_iris_images else 'questionnaire_only'
        
        # Store assessment in database
        async with get_db_connection() as conn:
            assessment_id = await conn.fetchval(
                """INSERT INTO comprehensive_assessments 
                   (patient_id, questionnaire_responses, questionnaire_scores, 
                    questionnaire_recommendations, iris_images, assessment_status,
                    practitioner_id, overall_wellness_score, integrated_recommendations)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                   RETURNING id""",
                patient_id,
                json.dumps(questionnaire_responses),
                json.dumps(questionnaire_scores),
                json.dumps(questionnaire_recommendations),
                json.dumps(iris_images) if has_iris_images else None,
                assessment_status,
                current_user["id"],
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
                    1.0,  # Will be updated with iridology data later
                    recommendation["recommended"],
                    recommendation["rationale"]
                )
        
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
async def get_patient_assessments(
    patient_id: int, 
    current_user: dict = Depends(verify_token)
):
    """Get all assessments for a specific patient"""
    try:
        async with get_db_connection() as conn:
            # Verify patient access
            if current_user.get("role") == "super_admin":
                patient = await conn.fetchrow(
                    "SELECT * FROM patients WHERE id = $1",
                    patient_id
                )
            else:
                patient = await conn.fetchrow(
                    """SELECT p.* FROM patients p 
                       WHERE p.id = $1 AND p.centre_id = $2""",
                    patient_id, current_user["centre_id"]
                )
            
            if not patient:
                raise HTTPException(status_code=403, detail="Access denied to this patient")
            
            # Get all assessments for patient
            assessments = await conn.fetch(
                """SELECT ca.id, ca.patient_id, ca.assessment_date, ca.assessment_status,
                          ca.overall_wellness_score, ca.created_at,
                          u.email as practitioner_email
                   FROM comprehensive_assessments ca
                   LEFT JOIN users u ON ca.practitioner_id = u.id
                   WHERE ca.patient_id = $1
                   ORDER BY ca.created_at DESC""",
                patient_id
            )
            
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
async def get_assessment_details(
    assessment_id: int, 
    current_user: dict = Depends(verify_token)
):
    """Get detailed assessment results including all scores and recommendations"""
    try:
        async with get_db_connection() as conn:
            # Get assessment with patient info
            if current_user.get("role") == "super_admin":
                assessment = await conn.fetchrow(
                    """SELECT ca.*, 
                              p.first_name, p.last_name, p.patient_number, p.date_of_birth,
                              u.email as practitioner_email
                       FROM comprehensive_assessments ca
                       JOIN patients p ON ca.patient_id = p.id
                       LEFT JOIN users u ON ca.practitioner_id = u.id
                       WHERE ca.id = $1""",
                    assessment_id
                )
            else:
                assessment = await conn.fetchrow(
                    """SELECT ca.*, 
                              p.first_name, p.last_name, p.patient_number, p.date_of_birth,
                              u.email as practitioner_email
                       FROM comprehensive_assessments ca
                       JOIN patients p ON ca.patient_id = p.id
                       LEFT JOIN users u ON ca.practitioner_id = u.id
                       WHERE ca.id = $1 AND p.centre_id = $2""",
                    assessment_id, current_user["centre_id"]
                )
            
            if not assessment:
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
            if assessment_dict.get('iris_images'):
                assessment_dict['iris_images'] = json.loads(assessment_dict['iris_images'])
            
            return {
                "success": True,
                "assessment": assessment_dict,
                "therapy_correlations": [dict(c) for c in correlations]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/assessments/centre/{centre_id}/recent")
async def get_centre_recent_assessments(
    centre_id: int,
    limit: int = 10,
    current_user: dict = Depends(verify_token)
):
    """Get recent assessments for a clinic/centre"""
    try:
        # Verify access
        if current_user.get("role") != "super_admin" and current_user.get("centre_id") != centre_id:
            raise HTTPException(status_code=403, detail="Access denied to this clinic")
        
        async with get_db_connection() as conn:
            assessments = await conn.fetch(
                """SELECT ca.id, ca.patient_id, ca.assessment_date, ca.assessment_status,
                          ca.overall_wellness_score, ca.created_at,
                          p.first_name, p.last_name, p.patient_number
                   FROM comprehensive_assessments ca
                   JOIN patients p ON ca.patient_id = p.id
                   WHERE p.centre_id = $1
                   ORDER BY ca.created_at DESC
                   LIMIT $2""",
                centre_id, limit
            )
            
            return {
                "success": True,
                "centre_id": centre_id,
                "total_returned": len(assessments),
                "assessments": [dict(a) for a in assessments]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/assessments/{assessment_id}")
async def delete_assessment(
    assessment_id: int,
    current_user: dict = Depends(verify_token)
):
    """Delete an assessment (admin only)"""
    try:
        if current_user.get("role") not in ["super_admin", "clinic_admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        async with get_db_connection() as conn:
            # Verify access
            if current_user.get("role") == "super_admin":
                assessment = await conn.fetchrow(
                    "SELECT id FROM comprehensive_assessments WHERE id = $1",
                    assessment_id
                )
            else:
                assessment = await conn.fetchrow(
                    """SELECT ca.id FROM comprehensive_assessments ca
                       JOIN patients p ON ca.patient_id = p.id
                       WHERE ca.id = $1 AND p.centre_id = $2""",
                    assessment_id, current_user["centre_id"]
                )
            
            if not assessment:
                raise HTTPException(status_code=404, detail="Assessment not found")
            
            # Delete assessment (cascade will handle related records)
            await conn.execute(
                "DELETE FROM comprehensive_assessments WHERE id = $1",
                assessment_id
            )
            
            return {
                "success": True,
                "message": "Assessment deleted successfully",
                "deleted_id": assessment_id
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
