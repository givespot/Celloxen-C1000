"""
SIMPLE ASSESSMENT API - AI-Powered Wellness Assessment System
Handles 35-question assessment with intelligent therapy matching
Uses Anthropic Claude API for comprehensive report generation
"""
from fastapi import APIRouter, HTTPException
import asyncpg
import os
import json
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime

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

# Anthropic API setup
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ==================== MODELS ====================
class AssessmentAnswer(BaseModel):
    question_id: int
    answer_index: int  # 0-4

class AssessmentSubmission(BaseModel):
    patient_id: int
    answers: List[AssessmentAnswer]

# ==================== RESPONSE OPTIONS ====================
RESPONSE_OPTIONS = {
    "scale": ["Very Low", "Low", "Moderate", "Good", "Excellent"],
    "frequency": ["Constantly", "Daily", "Few times a week", "Rarely", "Never"],
    "severity": ["Severe", "Moderate", "Mild", "Minimal", "None"],
    "quality": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
    "duration": ["Over 6 months", "3-6 months", "1-3 months", "Less than a month", "Not applicable"]
}

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
            response_options,
            question_order
        FROM assessment_questions
        ORDER BY question_order
    """)
    
    await conn.close()
    
    return {
        "questions": [
            {
                "id": q['id'],
                "therapy_domain": q['therapy_domain'],
                "question_text": q['question_text'],
                "question_type": q['question_type'],
                "response_options": json.loads(q['response_options']) if q['response_options'] else RESPONSE_OPTIONS.get(q['question_type'], RESPONSE_OPTIONS['scale']),
                "question_order": q['question_order']
            }
            for q in questions
        ]
    }

# ==================== AI REPORT GENERATION ====================
async def generate_ai_report(
    patient_info: Dict,
    questions_and_answers: List[Dict],
    domain_scores: Dict,
    therapies: List[Dict]
) -> Dict:
    """Generate comprehensive AI-powered assessment report using Claude API"""
    
    try:
        from anthropic import Anthropic
        
        if not ANTHROPIC_API_KEY:
            return {"success": False, "error": "AI API key not configured"}
        
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Format questions and answers
        qa_text = ""
        for i, qa in enumerate(questions_and_answers, 1):
            qa_text += f"\nQ{i}. {qa['question']}\n"
            qa_text += f"    Answer: {qa['answer']} (Score: {qa['score']}/100)\n"
        
        # Format therapies information
        therapies_text = ""
        for t in therapies:
            therapies_text += f"""
--- {t['therapy_code']}: {t['therapy_name']} ---
Subtitle: {t['subtitle']}
Description: {t['description'][:300]}...
Client Indicators: {json.dumps(t['client_indicators'][:5]) if isinstance(t['client_indicators'], list) else t['client_indicators']}
Short-term Benefits: {json.dumps(t['short_term_benefits'][:3]) if isinstance(t['short_term_benefits'], list) else t['short_term_benefits']}
Treatment Protocol: {t['recommended_sessions']} sessions, {t['session_frequency']}, {t['session_duration']}
"""
        
        prompt = f"""You are a senior wellness consultant at Celloxen Health, a UK-based bioelectronic therapy clinic. You specialise in comprehensive wellness assessment and therapy recommendations.

IMPORTANT: Use British English spelling throughout (e.g., optimise, programme, colour, centre, analyse).

PATIENT INFORMATION:
- Name: {patient_info.get('name', 'Patient')}
- Age: {patient_info.get('age', 'Not provided')}
- Gender: {patient_info.get('gender', 'Not provided')}

WELLNESS ASSESSMENT RESPONSES:
The patient completed a 35-question comprehensive wellness questionnaire covering 5 domains.
Scoring: 0 = Most concern (poor wellness), 100 = Optimal wellness

{qa_text}

DOMAIN SCORES (0-100, lower = more concern):
- Energy & Vitality (C-102): {domain_scores.get('energy', 0):.1f}%
- Comfort & Mobility (C-104): {domain_scores.get('comfort', 0):.1f}%
- Circulation & Heart (C-105): {domain_scores.get('circulation', 0):.1f}%
- Stress & Relaxation (C-107): {domain_scores.get('stress', 0):.1f}%
- Metabolic Balance (C-108): {domain_scores.get('metabolic', 0):.1f}%
- Overall Wellness: {domain_scores.get('overall', 0):.1f}%

AVAILABLE CELLOXEN THERAPIES:
{therapies_text}

ANALYSIS INSTRUCTIONS:
Based on the patient's responses and scores, provide a comprehensive wellness assessment report. Consider:
1. Lower scores indicate areas of greater concern requiring attention
2. Patterns in responses that suggest underlying wellness challenges
3. Which Celloxen therapies would best address the identified concerns
4. The priority order for therapy recommendations

Based on the patient's wellness concerns, also recommend 2-3 appropriate dietary supplements that may support their health goals. Choose supplements that are well-researched and commonly available.

Generate a detailed report in the following JSON format:
{{
    "executive_summary": "A 2-3 sentence overview of the patient's wellness status and key findings",
    
    "wellness_overview": {{
        "overall_status": "Excellent/Good/Fair/Needs Attention/Requires Support",
        "primary_concerns": ["List of top 3-5 identified health concerns based on responses"],
        "positive_indicators": ["List of wellness areas showing strength"]
    }},
    
    "domain_analysis": {{
        "energy": {{
            "status": "Status description",
            "key_findings": ["Specific findings from responses"],
            "concern_level": "Low/Moderate/High"
        }},
        "comfort": {{
            "status": "Status description", 
            "key_findings": ["Specific findings from responses"],
            "concern_level": "Low/Moderate/High"
        }},
        "circulation": {{
            "status": "Status description",
            "key_findings": ["Specific findings from responses"],
            "concern_level": "Low/Moderate/High"
        }},
        "stress": {{
            "status": "Status description",
            "key_findings": ["Specific findings from responses"],
            "concern_level": "Low/Moderate/High"
        }},
        "metabolic": {{
            "status": "Status description",
            "key_findings": ["Specific findings from responses"],
            "concern_level": "Low/Moderate/High"
        }}
    }},
    
    "therapy_recommendations": [
        {{
            "priority": 1,
            "therapy_code": "C-XXX",
            "therapy_name": "Name of therapy",
            "recommendation_reason": "Detailed explanation of why this therapy is recommended based on the patient's specific responses",
            "expected_benefits": ["List of expected benefits for this patient"],
            "treatment_plan": {{
                "sessions": number,
                "frequency": "frequency",
                "duration": "duration per session",
                "estimated_completion": "X weeks"
            }},
            "urgency": "Immediate/Soon/Maintenance"
        }}
    ],
    
    "lifestyle_recommendations": [
        "General wellness advice based on findings - use British English"
    ],
    
    "supplement_recommendations": [
        {{
            "name": "Name of supplement",
            "purpose": "Why this supplement may help based on findings",
            "suggested_dosage": "Typical dosage guidance",
            "notes": "Any important considerations"
        }}
    ],
    
    "follow_up_notes": "When to reassess and what to monitor",
    
    "disclaimer": "This assessment is for wellness support purposes only and does not constitute medical diagnosis. Supplement recommendations are for informational purposes only. Always consult with qualified healthcare professionals before starting any supplement regimen."
}}

Provide ONLY the JSON response, no additional text before or after."""

        # Call Claude API
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Parse response
        response_text = message.content[0].text
        
        # Clean and parse JSON
        cleaned = response_text.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        if cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        try:
            report = json.loads(cleaned.strip())
            return {"success": True, "report": report}
        except json.JSONDecodeError:
            return {"success": True, "report": {"raw_analysis": response_text}}
            
    except Exception as e:
        print(f"AI Report Generation Error: {str(e)}")
        return {"success": False, "error": str(e)}

# ==================== SUBMIT ASSESSMENT ====================
@router.post("/api/v1/assessment/submit")
async def submit_assessment(submission: AssessmentSubmission):
    """
    Submit completed 35-question assessment
    Calculate scores, generate AI report, and save to database
    """
    conn = await get_db()
    
    try:
        # Get all questions to validate and calculate scores
        questions = await conn.fetch("""
            SELECT id, therapy_domain, question_order, question_text, response_options
            FROM assessment_questions
            ORDER BY question_order
        """)
        
        # Validate we have 35 answers
        if len(submission.answers) != 35:
            raise HTTPException(
                status_code=400,
                detail=f"Expected 35 answers, got {len(submission.answers)}"
            )
        
        # Get patient info
        patient = await conn.fetchrow("""
            SELECT id, first_name, last_name, date_of_birth, gender
            FROM patients WHERE id = $1
        """, submission.patient_id)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Calculate age
        age = None
        if patient['date_of_birth']:
            today = datetime.now().date()
            dob = patient['date_of_birth']
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        # Calculate domain scores
        domain_scores = {
            'C-102': [],  # Energy (Q1-7)
            'C-104': [],  # Comfort (Q8-14)
            'C-105': [],  # Circulation (Q15-21)
            'C-107': [],  # Stress (Q22-28)
            'C-108': []   # Metabolic (Q29-35)
        }
        
        # Build questions and answers for AI
        questions_and_answers = []
        
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
            
            # Get answer text
            options = json.loads(question['response_options']) if question['response_options'] else ["Very Low", "Low", "Moderate", "Good", "Excellent"]
            answer_text = options[answer.answer_index] if answer.answer_index < len(options) else f"Option {answer.answer_index}"
            
            questions_and_answers.append({
                "question": question['question_text'],
                "answer": answer_text,
                "score": score,
                "domain": domain
            })
        
        # Calculate average for each domain
        energy_score = sum(domain_scores['C-102']) / len(domain_scores['C-102'])
        comfort_score = sum(domain_scores['C-104']) / len(domain_scores['C-104'])
        circulation_score = sum(domain_scores['C-105']) / len(domain_scores['C-105'])
        stress_score = sum(domain_scores['C-107']) / len(domain_scores['C-107'])
        metabolic_score = sum(domain_scores['C-108']) / len(domain_scores['C-108'])
        
        # Overall score is average of all domains
        overall_score = (energy_score + comfort_score + circulation_score + 
                        stress_score + metabolic_score) / 5
        
        # Get therapies from database
        therapies = await conn.fetch("""
            SELECT therapy_code, therapy_name, subtitle, description,
                   primary_support_areas, client_indicators, 
                   short_term_benefits, long_term_benefits,
                   recommended_sessions, session_frequency, session_duration
            FROM therapies
            WHERE is_active = true
            ORDER BY therapy_code
        """)
        
        therapies_list = []
        for t in therapies:
            therapies_list.append({
                'therapy_code': t['therapy_code'],
                'therapy_name': t['therapy_name'],
                'subtitle': t['subtitle'],
                'description': t['description'],
                'client_indicators': t['client_indicators'] if isinstance(t['client_indicators'], list) else json.loads(t['client_indicators']) if t['client_indicators'] else [],
                'primary_support_areas': t['primary_support_areas'] if isinstance(t['primary_support_areas'], list) else json.loads(t['primary_support_areas']) if t['primary_support_areas'] else [],
                'short_term_benefits': t['short_term_benefits'] if isinstance(t['short_term_benefits'], list) else json.loads(t['short_term_benefits']) if t['short_term_benefits'] else [],
                'long_term_benefits': t['long_term_benefits'] if isinstance(t['long_term_benefits'], list) else json.loads(t['long_term_benefits']) if t['long_term_benefits'] else [],
                'recommended_sessions': t['recommended_sessions'],
                'session_frequency': t['session_frequency'],
                'session_duration': t['session_duration']
            })
        
        # Prepare patient info for AI
        patient_info = {
            'name': f"{patient['first_name']} {patient['last_name']}",
            'age': age,
            'gender': patient['gender']
        }
        
        # Prepare domain scores for AI
        scores_for_ai = {
            'energy': energy_score,
            'comfort': comfort_score,
            'circulation': circulation_score,
            'stress': stress_score,
            'metabolic': metabolic_score,
            'overall': overall_score
        }
        
        # Generate AI report
        print(f"Generating AI report for patient {submission.patient_id}...")
        ai_result = await generate_ai_report(
            patient_info,
            questions_and_answers,
            scores_for_ai,
            therapies_list
        )
        
        ai_report = ai_result.get('report') if ai_result.get('success') else None
        
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
                ai_report,
                report_generated_at,
                status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'completed')
            RETURNING id
        """, submission.patient_id, energy_score, comfort_score,
            circulation_score, stress_score, metabolic_score, overall_score,
            json.dumps(ai_report) if ai_report else None,
            datetime.now() if ai_report else None)
        
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
            "report": ai_report,
            "message": "Assessment completed successfully!"
        }
        
    except HTTPException:
        await conn.close()
        raise
    except Exception as e:
        await conn.close()
        print(f"Assessment Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== GET PATIENT'S LATEST ASSESSMENT ====================
@router.get("/api/v1/assessment/patient/{patient_id}/latest")
async def get_patient_latest_assessment(patient_id: int):
    """Get patient's most recent assessment with scores and AI report"""
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
            "report": json.loads(assessment['ai_report']) if assessment['ai_report'] else None,
            "report_generated_at": str(assessment['report_generated_at']) if assessment['report_generated_at'] else None,
            "status": assessment['status']
        }
    }

# ==================== GET ASSESSMENT BY ID ====================
@router.get("/api/v1/assessment/{assessment_id}")
async def get_assessment_by_id(assessment_id: int):
    """Get specific assessment with full details and AI report"""
    conn = await get_db()
    
    assessment = await conn.fetchrow("""
        SELECT pa.*, p.first_name, p.last_name, p.patient_number
        FROM patient_assessments pa
        JOIN patients p ON pa.patient_id = p.id
        WHERE pa.id = $1
    """, assessment_id)
    
    if not assessment:
        await conn.close()
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Get all responses with questions
    responses = await conn.fetch("""
        SELECT ar.*, aq.question_text, aq.therapy_domain, aq.response_options
        FROM assessment_responses ar
        JOIN assessment_questions aq ON ar.question_id = aq.id
        WHERE ar.assessment_id = $1
        ORDER BY aq.question_order
    """, assessment_id)
    
    await conn.close()
    
    # Format responses
    formatted_responses = []
    for r in responses:
        options = json.loads(r['response_options']) if r['response_options'] else ["Very Low", "Low", "Moderate", "Good", "Excellent"]
        answer_text = options[r['answer_index']] if r['answer_index'] < len(options) else f"Option {r['answer_index']}"
        formatted_responses.append({
            "question": r['question_text'],
            "domain": r['therapy_domain'],
            "answer": answer_text,
            "answer_index": r['answer_index']
        })
    
    return {
        "success": True,
        "assessment": {
            "id": assessment['id'],
            "patient": {
                "id": assessment['patient_id'],
                "name": f"{assessment['first_name']} {assessment['last_name']}",
                "patient_number": assessment['patient_number']
            },
            "date": str(assessment['assessment_date']),
            "scores": {
                "energy": float(assessment['energy_score']),
                "comfort": float(assessment['comfort_score']),
                "circulation": float(assessment['circulation_score']),
                "stress": float(assessment['stress_score']),
                "metabolic": float(assessment['metabolic_score']),
                "overall": float(assessment['overall_score'])
            },
            "responses": formatted_responses,
            "report": json.loads(assessment['ai_report']) if assessment['ai_report'] else None,
            "report_generated_at": str(assessment['report_generated_at']) if assessment['report_generated_at'] else None,
            "status": assessment['status']
        }
    }

# ==================== PDF REPORT GENERATION ====================
from fastapi.responses import Response

@router.get("/api/v1/assessment/{assessment_id}/report/pdf")
async def download_assessment_pdf_report(assessment_id: int):
    """Generate and download PDF wellness report"""
    conn = await get_db()
    
    try:
        # Get assessment with AI report
        assessment = await conn.fetchrow("""
            SELECT * FROM patient_assessments WHERE id = $1
        """, assessment_id)
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Get patient
        patient = await conn.fetchrow("""
            SELECT * FROM patients WHERE id = $1
        """, assessment['patient_id'])
        
        await conn.close()
        
        # Try to use pdf_report_generator if available
        try:
            from pdf_report_generator import generate_pdf_report
            pdf_bytes = generate_pdf_report(dict(patient), dict(assessment))
            
            filename = f"wellness_report_{patient['patient_number']}_{assessment_id}.pdf"
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
        except ImportError:
            raise HTTPException(status_code=500, detail="PDF generator not available")
            
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

