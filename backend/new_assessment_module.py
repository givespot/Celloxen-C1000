"""
CellOxen Health Portal - New Assessment Module
Clean implementation with proper scoring
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncpg
from datetime import datetime
import os

router = APIRouter(prefix="/api/v1/new-assessment", tags=["new-assessment"])

# ================================================================
# PYDANTIC MODELS
# ================================================================

class StartAssessmentRequest(BaseModel):
    patient_id: int
    practitioner_id: int
    clinic_id: int

class AnswerSubmission(BaseModel):
    assessment_id: int
    question_id: int
    answer_text: str
    answer_score: int

class CompleteAssessmentRequest(BaseModel):
    assessment_id: int

# ================================================================
# DATABASE CONNECTION
# ================================================================

async def get_db():
    return await asyncpg.connect(
        host="localhost",
        port=5432,
        user="celloxen_user",
        password=os.getenv("DB_PASSWORD"),
        database="celloxen_portal"
    )

# ================================================================
# 35 WELLNESS QUESTIONS (5 domains x 7 questions)
# ================================================================

ASSESSMENT_QUESTIONS = {
    "vitality_energy": [
        {
            "id": 1,
            "domain": "vitality_energy",
            "text": "How would you rate your overall energy levels throughout the day?",
            "options": ["Very Low", "Low", "Moderate", "Good", "Excellent"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 2,
            "domain": "vitality_energy",
            "text": "How often do you feel fatigued or exhausted?",
            "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 3,
            "domain": "vitality_energy",
            "text": "How well do you sleep at night?",
            "options": ["Very Poorly", "Poorly", "Fair", "Well", "Very Well"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 4,
            "domain": "vitality_energy",
            "text": "How would you describe your morning alertness?",
            "options": ["Very Sluggish", "Sluggish", "Moderate", "Alert", "Very Alert"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 5,
            "domain": "vitality_energy",
            "text": "How often do you need caffeine or stimulants?",
            "options": ["Constantly", "Frequently", "Occasionally", "Rarely", "Never"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 6,
            "domain": "vitality_energy",
            "text": "How is your ability to maintain focus and concentration?",
            "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 7,
            "domain": "vitality_energy",
            "text": "How would you rate your overall vitality?",
            "options": ["Very Low", "Low", "Moderate", "High", "Very High"],
            "scores": [0, 25, 50, 75, 100]
        }
    ],
    "comfort_mobility": [
        {
            "id": 8,
            "domain": "comfort_mobility",
            "text": "How would you rate your overall physical comfort?",
            "options": ["Very Uncomfortable", "Uncomfortable", "Neutral", "Comfortable", "Very Comfortable"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 9,
            "domain": "comfort_mobility",
            "text": "Do you experience any chronic pain or discomfort?",
            "options": ["Severe", "Moderate", "Mild", "Minimal", "None"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 10,
            "domain": "comfort_mobility",
            "text": "How is your flexibility and range of motion?",
            "options": ["Very Limited", "Limited", "Moderate", "Good", "Excellent"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 11,
            "domain": "comfort_mobility",
            "text": "How would you describe your balance and coordination?",
            "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 12,
            "domain": "comfort_mobility",
            "text": "How often do you experience muscle stiffness?",
            "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 13,
            "domain": "comfort_mobility",
            "text": "How is your physical endurance for daily activities?",
            "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 14,
            "domain": "comfort_mobility",
            "text": "How would you rate your overall mobility?",
            "options": ["Very Limited", "Limited", "Moderate", "Good", "Excellent"],
            "scores": [0, 25, 50, 75, 100]
        }
    ],
    "circulation_heart": [
        {
            "id": 15,
            "domain": "circulation_heart",
            "text": "How would you describe your circulation (cold hands/feet)?",
            "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 16,
            "domain": "circulation_heart",
            "text": "Do you experience shortness of breath with mild activity?",
            "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 17,
            "domain": "circulation_heart",
            "text": "How is your blood pressure (as far as you know)?",
            "options": ["Very High", "High", "Normal", "Optimal", "Perfect"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 18,
            "domain": "circulation_heart",
            "text": "How often do you experience heart palpitations?",
            "options": ["Frequently", "Often", "Sometimes", "Rarely", "Never"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 19,
            "domain": "circulation_heart",
            "text": "How is your recovery time after physical activity?",
            "options": ["Very Slow", "Slow", "Moderate", "Fast", "Very Fast"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 20,
            "domain": "circulation_heart",
            "text": "Do you experience swelling in legs or ankles?",
            "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 21,
            "domain": "circulation_heart",
            "text": "How would you rate your cardiovascular fitness?",
            "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
            "scores": [0, 25, 50, 75, 100]
        }
    ],
    "stress_relaxation": [
        {
            "id": 22,
            "domain": "stress_relaxation",
            "text": "How would you rate your current stress levels?",
            "options": ["Extreme", "High", "Moderate", "Low", "Very Low"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 23,
            "domain": "stress_relaxation",
            "text": "How often do you feel anxious or worried?",
            "options": ["Constantly", "Often", "Sometimes", "Rarely", "Never"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 24,
            "domain": "stress_relaxation",
            "text": "How well can you relax when needed?",
            "options": ["Unable", "With Difficulty", "Moderately", "Easily", "Very Easily"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 25,
            "domain": "stress_relaxation",
            "text": "How is your emotional stability throughout the day?",
            "options": ["Very Unstable", "Unstable", "Moderate", "Stable", "Very Stable"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 26,
            "domain": "stress_relaxation",
            "text": "How often do you feel overwhelmed?",
            "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 27,
            "domain": "stress_relaxation",
            "text": "How would you describe your overall mood?",
            "options": ["Very Low", "Low", "Neutral", "Positive", "Very Positive"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 28,
            "domain": "stress_relaxation",
            "text": "How well do you cope with daily challenges?",
            "options": ["Very Poorly", "Poorly", "Adequately", "Well", "Very Well"],
            "scores": [0, 25, 50, 75, 100]
        }
    ],
    "immune_digestive": [
        {
            "id": 29,
            "domain": "immune_digestive",
            "text": "How often do you get sick (colds, flu, etc.)?",
            "options": ["Very Often", "Often", "Sometimes", "Rarely", "Very Rarely"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 30,
            "domain": "immune_digestive",
            "text": "How is your digestive comfort after meals?",
            "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 31,
            "domain": "immune_digestive",
            "text": "How regular are your bowel movements?",
            "options": ["Very Irregular", "Irregular", "Somewhat Regular", "Regular", "Very Regular"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 32,
            "domain": "immune_digestive",
            "text": "Do you experience bloating or gas?",
            "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 33,
            "domain": "immune_digestive",
            "text": "How is your appetite and relationship with food?",
            "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 34,
            "domain": "immune_digestive",
            "text": "How would you rate your body's healing ability?",
            "options": ["Very Slow", "Slow", "Moderate", "Fast", "Very Fast"],
            "scores": [0, 25, 50, 75, 100]
        },
        {
            "id": 35,
            "domain": "immune_digestive",
            "text": "How would you rate your overall immune health?",
            "options": ["Very Weak", "Weak", "Moderate", "Strong", "Very Strong"],
            "scores": [0, 25, 50, 75, 100]
        }
    ]
}

# ================================================================
# API ENDPOINTS
# ================================================================

@router.get("/questions")
async def get_all_questions():
    """Get all 35 assessment questions"""
    # Flatten all questions into single list
    all_questions = []
    for domain, questions in ASSESSMENT_QUESTIONS.items():
        all_questions.extend(questions)
    
    return {
        "total_questions": len(all_questions),
        "questions": all_questions,
        "domains": list(ASSESSMENT_QUESTIONS.keys())
    }

@router.post("/start")
async def start_assessment(request: StartAssessmentRequest):
    """Start a new assessment"""
    conn = await get_db()
    try:
        # Create assessment record
        assessment_id = await conn.fetchval(
            """
            INSERT INTO comprehensive_assessments (
                patient_id, 
                practitioner_id, 
                clinic_id,
                assessment_date,
                status,
                overall_wellness_score,
                questionnaire_scores
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
            """,
            request.patient_id,
            request.practitioner_id,
            request.clinic_id,
            datetime.now(),
            'in_progress',
            0.0,
            {}
        )
        
        return {
            "assessment_id": assessment_id,
            "status": "started",
            "total_questions": 35
        }
    finally:
        await conn.close()

@router.post("/answer")
async def submit_answer(answer: AnswerSubmission):
    """Submit answer for a single question"""
    conn = await get_db()
    try:
        # Get current responses
        current_responses = await conn.fetchval(
            "SELECT questionnaire_responses FROM comprehensive_assessments WHERE id = $1",
            answer.assessment_id
        )
        
        if current_responses is None:
            current_responses = {}
        
        # Add new answer
        current_responses[str(answer.question_id)] = {
            "answer_text": answer.answer_text,
            "score": answer.answer_score
        }
        
        # Update database
        await conn.execute(
            """
            UPDATE comprehensive_assessments 
            SET questionnaire_responses = $1
            WHERE id = $2
            """,
            current_responses,
            answer.assessment_id
        )
        
        return {
            "success": True,
            "questions_answered": len(current_responses),
            "questions_remaining": 35 - len(current_responses)
        }
    finally:
        await conn.close()

@router.post("/complete")
async def complete_assessment(request: CompleteAssessmentRequest):
    """Calculate scores and complete assessment"""
    conn = await get_db()
    try:
        # Get all responses
        responses = await conn.fetchval(
            "SELECT questionnaire_responses FROM comprehensive_assessments WHERE id = $1",
            request.assessment_id
        )
        
        if not responses or len(responses) < 35:
            raise HTTPException(
                status_code=400,
                detail=f"Assessment incomplete: {len(responses) if responses else 0}/35 questions answered"
            )
        
        # Calculate domain scores
        domain_scores = {}
        
        for domain, questions in ASSESSMENT_QUESTIONS.items():
            domain_total = 0
            questions_in_domain = len(questions)
            
            for question in questions:
                q_id = str(question["id"])
                if q_id in responses:
                    domain_total += responses[q_id]["score"]
            
            # Calculate percentage for this domain
            domain_scores[domain] = round((domain_total / (questions_in_domain * 100)) * 100, 1)
        
        # Calculate overall wellness score
        overall_score = round(sum(domain_scores.values()) / len(domain_scores), 1)
        
        # Update assessment
        await conn.execute(
            """
            UPDATE comprehensive_assessments
            SET status = 'completed',
                overall_wellness_score = $1,
                questionnaire_scores = $2,
                assessment_date = $3
            WHERE id = $4
            """,
            overall_score,
            domain_scores,
            datetime.now(),
            request.assessment_id
        )
        
        return {
            "assessment_id": request.assessment_id,
            "status": "completed",
            "overall_score": overall_score,
            "domain_scores": domain_scores
        }
    finally:
        await conn.close()

@router.get("/results/{assessment_id}")
async def get_results(assessment_id: int):
    """Get complete assessment results"""
    conn = await get_db()
    try:
        result = await conn.fetchrow(
            """
            SELECT 
                ca.id,
                ca.patient_id,
                ca.overall_wellness_score,
                ca.questionnaire_scores,
                ca.assessment_date,
                ca.status,
                p.first_name || ' ' || p.last_name as patient_name,
                p.patient_number
            FROM comprehensive_assessments ca
            JOIN patients p ON ca.patient_id = p.id
            WHERE ca.id = $1
            """,
            assessment_id
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        return dict(result)
    finally:
        await conn.close()
