"""
CELLOXEN HEALTH PORTAL - NEW ASSESSMENT MODULE
Clean, simple, working assessment system
Created: November 14, 2025
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncpg
import json

router = APIRouter(prefix="/api/v1/new-assessment", tags=["New Assessment"])

# ============================================================================
# ASSESSMENT QUESTIONS - 35 QUESTIONS, 5 DOMAINS
# ============================================================================

ASSESSMENT_QUESTIONS = {
    "vitality_energy": {
        "domain_name": "Vitality & Energy Support",
        "therapy_code": "C-102",
        "questions": [
            {"id": 1, "text": "How would you rate your overall energy levels throughout the day?", "options": ["Very Low", "Low", "Moderate", "Good", "Excellent"], "scores": [0, 25, 50, 75, 100]},
            {"id": 2, "text": "How often do you experience fatigue or tiredness?", "options": ["Constantly", "Daily", "Few times a week", "Rarely", "Never"], "scores": [0, 25, 50, 75, 100]},
            {"id": 3, "text": "Do you experience afternoon energy crashes?", "options": ["Always", "Often", "Sometimes", "Rarely", "Never"], "scores": [0, 25, 50, 75, 100]},
            {"id": 4, "text": "How well do you recover after physical activity?", "options": ["Very Poorly", "Poorly", "Moderately", "Well", "Very Well"], "scores": [0, 25, 50, 75, 100]},
            {"id": 5, "text": "How would you describe your mental clarity and focus?", "options": ["Very Foggy", "Foggy", "Average", "Clear", "Very Clear"], "scores": [0, 25, 50, 75, 100]},
            {"id": 6, "text": "How many hours of quality sleep do you get per night?", "options": ["Less than 5", "5-6 hours", "6-7 hours", "7-8 hours", "8+ hours"], "scores": [0, 25, 50, 75, 100]},
            {"id": 7, "text": "How often do you feel motivated to engage in daily activities?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 25, 50, 75, 100]}
        ]
    },
    "comfort_mobility": {
        "domain_name": "Comfort & Mobility Support",
        "therapy_code": "C-104",
        "questions": [
            {"id": 8, "text": "How would you rate your current pain levels?", "options": ["Severe", "Moderate-Severe", "Moderate", "Mild", "None"], "scores": [0, 25, 50, 75, 100]},
            {"id": 9, "text": "How does pain affect your daily activities?", "options": ["Severely limits", "Significantly limits", "Moderately limits", "Slightly limits", "No limitation"], "scores": [0, 25, 50, 75, 100]},
            {"id": 10, "text": "How stiff do your joints feel in the morning?", "options": ["Extremely stiff", "Very stiff", "Moderately stiff", "Slightly stiff", "Not stiff"], "scores": [0, 25, 50, 75, 100]},
            {"id": 11, "text": "How is your range of motion in affected areas?", "options": ["Very Limited", "Limited", "Moderate", "Good", "Excellent"], "scores": [0, 25, 50, 75, 100]},
            {"id": 12, "text": "How often do you experience muscle tension or spasms?", "options": ["Constantly", "Daily", "Few times a week", "Rarely", "Never"], "scores": [0, 25, 50, 75, 100]},
            {"id": 13, "text": "How well can you perform physical tasks (walking, climbing stairs)?", "options": ["Very Difficult", "Difficult", "Manageable", "Easy", "Very Easy"], "scores": [0, 25, 50, 75, 100]},
            {"id": 14, "text": "How much does discomfort interfere with your sleep?", "options": ["Severely", "Significantly", "Moderately", "Slightly", "Not at all"], "scores": [0, 25, 50, 75, 100]}
        ]
    },
    "circulation_heart": {
        "domain_name": "Circulation & Heart Wellness",
        "therapy_code": "C-105",
        "questions": [
            {"id": 15, "text": "How often do you experience cold hands or feet?", "options": ["Constantly", "Very Often", "Sometimes", "Rarely", "Never"], "scores": [0, 25, 50, 75, 100]},
            {"id": 16, "text": "Do you experience swelling in your legs, ankles, or feet?", "options": ["Always", "Often", "Sometimes", "Rarely", "Never"], "scores": [0, 25, 50, 75, 100]},
            {"id": 17, "text": "How would you describe your energy during physical exertion?", "options": ["Extremely Limited", "Very Limited", "Moderate", "Good", "Excellent"], "scores": [0, 25, 50, 75, 100]},
            {"id": 18, "text": "How often do you experience shortness of breath during normal activities?", "options": ["Very Often", "Often", "Sometimes", "Rarely", "Never"], "scores": [0, 25, 50, 75, 100]},
            {"id": 19, "text": "Do you experience irregular heartbeat or palpitations?", "options": ["Frequently", "Often", "Sometimes", "Rarely", "Never"], "scores": [0, 25, 50, 75, 100]},
            {"id": 20, "text": "How would you rate your overall cardiovascular fitness?", "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"], "scores": [0, 25, 50, 75, 100]},
            {"id": 21, "text": "How often do you feel dizzy or lightheaded when standing?", "options": ["Very Often", "Often", "Sometimes", "Rarely", "Never"], "scores": [0, 25, 50, 75, 100]}
        ]
    },
    "stress_relaxation": {
        "domain_name": "Stress & Relaxation Support",
        "therapy_code": "C-107",
        "questions": [
            {"id": 22, "text": "How would you rate your current stress levels?", "options": ["Extreme", "High", "Moderate", "Low", "Very Low"], "scores": [0, 25, 50, 75, 100]},
            {"id": 23, "text": "How often do you feel anxious or worried?", "options": ["Constantly", "Very Often", "Sometimes", "Rarely", "Never"], "scores": [0, 25, 50, 75, 100]},
            {"id": 24, "text": "How well do you fall asleep at night?", "options": ["Very Poorly", "Poorly", "Moderately", "Well", "Very Well"], "scores": [0, 25, 50, 75, 100]},
            {"id": 25, "text": "How would you describe the quality of your sleep?", "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"], "scores": [0, 25, 50, 75, 100]},
            {"id": 26, "text": "How often do you wake up feeling refreshed?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 25, 50, 75, 100]},
            {"id": 27, "text": "How well can you relax and unwind?", "options": ["Very Difficult", "Difficult", "Moderate", "Easy", "Very Easy"], "scores": [0, 25, 50, 75, 100]},
            {"id": 28, "text": "How often do you experience tension headaches?", "options": ["Very Often", "Often", "Sometimes", "Rarely", "Never"], "scores": [0, 25, 50, 75, 100]}
        ]
    },
    "immune_digestive": {
        "domain_name": "Immune & Digestive Wellness",
        "therapy_code": "C-108",
        "questions": [
            {"id": 29, "text": "How often do you experience digestive discomfort?", "options": ["Daily", "Several times a week", "Weekly", "Rarely", "Never"], "scores": [0, 25, 50, 75, 100]},
            {"id": 30, "text": "How would you describe your bowel movements?", "options": ["Very Irregular", "Irregular", "Somewhat Regular", "Regular", "Very Regular"], "scores": [0, 25, 50, 75, 100]},
            {"id": 31, "text": "How often do you get colds or infections?", "options": ["Very Frequently", "Frequently", "Occasionally", "Rarely", "Almost Never"], "scores": [0, 25, 50, 75, 100]},
            {"id": 32, "text": "How quickly do you recover from illnesses?", "options": ["Very Slowly", "Slowly", "Average", "Quickly", "Very Quickly"], "scores": [0, 25, 50, 75, 100]},
            {"id": 33, "text": "Do you experience food sensitivities or allergies?", "options": ["Many/Severe", "Several", "A Few", "Rare", "None"], "scores": [0, 25, 50, 75, 100]},
            {"id": 34, "text": "How would you rate your appetite and eating patterns?", "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"], "scores": [0, 25, 50, 75, 100]},
            {"id": 35, "text": "How often do you experience bloating or gas?", "options": ["Daily", "Several times a week", "Weekly", "Rarely", "Never"], "scores": [0, 25, 50, 75, 100]}
        ]
    }
}

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AssessmentStart(BaseModel):
    patient_id: int
    practitioner_id: Optional[int] = None

class AnswerSubmit(BaseModel):
    assessment_id: int
    question_id: int
    answer_text: str
    answer_score: int

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/questions")
async def get_all_questions():
    """Get all 35 questions structured by domain"""
    return {
        "success": True,
        "total_questions": 35,
        "domains": ASSESSMENT_QUESTIONS
    }

@router.post("/start")
async def start_assessment(data: AssessmentStart):
    """Start a new assessment session"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        assessment_id = await conn.fetchval(
            """INSERT INTO comprehensive_assessments 
               (patient_id, assessment_status, created_at)
               VALUES ($1, 'in_progress', NOW())
               RETURNING id""",
            data.patient_id
        )
        
        await conn.close()
        
        return {
            "success": True,
            "assessment_id": assessment_id,
            "total_questions": 35,
            "message": "Assessment started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answer")
async def submit_answer(data: AnswerSubmit):
    """Submit answer for a single question - uses pure PostgreSQL JSONB operations"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        # Use PostgreSQL's JSONB operators directly - no Python dict manipulation
        await conn.execute(
            """UPDATE comprehensive_assessments
               SET questionnaire_responses = 
                   COALESCE(questionnaire_responses, '{}'::jsonb) || 
                   $2::jsonb
               WHERE id = $1""",
            data.assessment_id,
            json.dumps({f"q{data.question_id}": {"answer": data.answer_text, "score": data.answer_score}})
        )
        
        # Count answers
        count_result = await conn.fetchval(
            """SELECT (SELECT COUNT(*) FROM jsonb_object_keys(
                   COALESCE(questionnaire_responses, '{}'::jsonb)
               )) FROM comprehensive_assessments WHERE id = $1""",
            data.assessment_id
        )
        
        await conn.close()
        
        return {
            "success": True,
            "questions_answered": count_result or 0,
            "total_questions": 35
        }
        
    except Exception as e:
        import traceback
        print(f"ERROR in submit_answer: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete")
async def complete_assessment(assessment_id: int):
    """Calculate scores and generate recommendations"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        responses_json = await conn.fetchval(
            "SELECT questionnaire_responses FROM comprehensive_assessments WHERE id = $1",
            assessment_id
        )
        
        if not responses_json:
            await conn.close()
            raise HTTPException(status_code=400, detail="No responses found")
        
        # Parse JSON if it's a string
        if isinstance(responses_json, str):
            import json as json_lib
            responses = json_lib.loads(responses_json)
        else:
            responses = responses_json
        
        # Work with responses dict
        domain_scores = {}
        for domain_key, domain_data in ASSESSMENT_QUESTIONS.items():
            questions = domain_data["questions"]
            total_score = 0
            answered = 0
            
            for q in questions:
                q_key = f"q{q['id']}"
                if q_key in responses:
                    total_score += int(responses[q_key]['score'])
                    answered += 1
            
            if answered > 0:
                percentage = (total_score / (answered * 100)) * 100
                domain_scores[domain_key] = {
                    "domain_name": domain_data["domain_name"],
                    "therapy_code": domain_data["therapy_code"],
                    "score": round(percentage, 1),
                    "questions_answered": answered,
                    "total_questions": len(questions)
                }
        
        overall_score = sum(d["score"] for d in domain_scores.values()) / len(domain_scores) if domain_scores else 0.0
        
        await conn.execute(
            """UPDATE comprehensive_assessments
               SET questionnaire_scores = $2::jsonb,
                   overall_wellness_score = $3,
                   assessment_status = 'completed',
                   assessment_date = NOW()
               WHERE id = $1""",
            assessment_id,
            json.dumps(domain_scores),
            round(overall_score, 1)
        )
        
        await conn.close()
        
        return {
            "success": True,
            "assessment_id": assessment_id,
            "overall_wellness_score": round(overall_score, 1),
            "domain_scores": domain_scores
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR in complete_assessment: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{assessment_id}")
async def get_results(assessment_id: int):
    """Get assessment results"""
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        result = await conn.fetchrow(
            """SELECT 
                a.*,
                p.first_name, p.last_name, p.patient_number
               FROM comprehensive_assessments a
               JOIN patients p ON a.patient_id = p.id
               WHERE a.id = $1""",
            assessment_id
        )
        
        await conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        return {
            "success": True,
            "assessment": dict(result)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
