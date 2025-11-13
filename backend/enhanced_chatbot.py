"""
CELLOXEN ENHANCED CHATBOT - Fixed to match actual database schema
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime
import json
import asyncpg

router = APIRouter()

# Database connection helper
async def get_db_conn():
    return await asyncpg.connect(
        host="localhost", port=5432, user="celloxen_user",
        password="CelloxenSecure2025", database="celloxen_portal"
    )

# Simple auth helper
async def get_current_user():
    return {"id": 1, "email": "admin@celloxen.com", "role": "super_admin"}

# Models
class ChatSessionStart(BaseModel):
    patient_id: int
    context: Optional[Dict[str, Any]] = None

class ChatMessage(BaseModel):
    message: str

@router.post("/chatbot/sessions/start")
async def start_chatbot_session(data: ChatSessionStart, request: Request):
    """Start new chatbot session"""
    
    user = await get_current_user()
    conn = await get_db_conn()
    
    try:
        # Get patient info
        patient = await conn.fetchrow(
            "SELECT id, first_name, last_name FROM patients WHERE id = $1",
            data.patient_id
        )
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get assessment info
        assessment = await conn.fetchrow("""
            SELECT id, overall_wellness_score, questionnaire_completed, 
                   iridology_completed, questionnaire_scores
            FROM comprehensive_assessments
            WHERE patient_id = $1
            ORDER BY created_at DESC LIMIT 1
        """, data.patient_id)
        
        if not assessment:
            raise HTTPException(status_code=404, detail="No assessment found")
        
        # Create session with actual schema
        session_token = str(uuid.uuid4())
        session_id = await conn.fetchval("""
            INSERT INTO chatbot_sessions (
                session_token, patient_id, assessment_id, practitioner_id,
                current_stage, status
            ) VALUES ($1, $2, $3, $4, 'contraindication', 'active')
            RETURNING id
        """, session_token, data.patient_id, assessment['id'], user['id'])
        
        # Create greeting
        patient_name = f"{patient['first_name']} {patient['last_name']}"
        wellness_score = float(assessment['overall_wellness_score'] or 0)
        
        greeting = f"""Hello! Welcome. I understand we are looking at {patient_name}'s records. Let me check the records...

✅ Records loaded successfully.

I can see {patient['first_name']} has completed the initial questionnaire with a wellness score of {wellness_score:.1f}%.

Before we proceed with therapy, I need to confirm there are no contraindications. Please ask {patient['first_name']} the following questions:

1. Do you have any heart conditions or heart disease?
2. Do you have a pacemaker fitted?

These conditions would make the Celloxen therapy unsuitable.

Please confirm: Are there any contraindications? (Reply with: "No contraindications" or provide details if yes)"""
        
        # Save message with actual schema
        await conn.execute("""
            INSERT INTO chatbot_messages (
                session_id, sender_type, message_type, message_text
            ) VALUES ($1, 'assistant', 'greeting', $2)
        """, session_id, greeting)
        
        return {
            "session_id": session_token,
            "patient_id": data.patient_id,
            "patient_name": patient_name,
            "initial_message": greeting,
            "conversation_stage": "contraindication"
        }
    
    finally:
        await conn.close()

@router.post("/chatbot/sessions/{session_token}/message")
async def send_chatbot_message(session_token: str, data: ChatMessage, request: Request):
    """Handle chatbot messages"""
    
    conn = await get_db_conn()
    
    try:
        # Get session by token
        session = await conn.fetchrow("""
            SELECT cs.id, cs.current_stage, cs.assessment_id, cs.patient_id,
                   p.first_name, ca.questionnaire_scores
            FROM chatbot_sessions cs
            JOIN patients p ON cs.patient_id = p.id
            LEFT JOIN comprehensive_assessments ca ON cs.assessment_id = ca.id
            WHERE cs.session_token = $1
        """, session_token)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Save user message
        await conn.execute("""
            INSERT INTO chatbot_messages (
                session_id, sender_type, message_type, message_text
            ) VALUES ($1, 'user', 'response', $2)
        """, session['id'], data.message)
        
        stage = session['current_stage']
        patient_name = session['first_name']
        
        # Handle contraindication stage
        if stage == 'contraindication':
            if 'no contraindication' in data.message.lower():
                # Save contraindication check
                await conn.execute("""
                    INSERT INTO contraindication_checks (
                        assessment_id, patient_id, heart_condition, 
                        pacemaker_fitted, has_contraindications
                    ) VALUES ($1, $2, FALSE, FALSE, FALSE)
                """, session['assessment_id'], session['patient_id'])
                
                response = f"""Thank you for confirming no contraindications.

Next Step: IRIDOLOGY ASSESSMENT

Please click the 'CAPTURE IMAGES' button in the Iridology module to capture {patient_name}'s iris images."""
                
                # Update session stage
                await conn.execute("""
                    UPDATE chatbot_sessions
                    SET current_stage = 'iridology'
                    WHERE id = $1
                """, session['id'])
                
                # Save response
                await conn.execute("""
                    INSERT INTO chatbot_messages (
                        session_id, sender_type, message_type, message_text
                    ) VALUES ($1, 'assistant', 'instruction', $2)
                """, session['id'], response)
                
                return {"response": response, "conversation_stage": "iridology"}
        
        return {"response": "I'm processing your message...", "conversation_stage": stage}
    
    finally:
        await conn.close()

