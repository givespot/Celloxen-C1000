"""
Chatbot Assessment API
Handles the in-clinic chatbot-guided comprehensive assessment
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import psycopg2
from ai_response_handler import AIResponseHandler
import psycopg2.extras
import secrets
from datetime import datetime
import json

router = APIRouter()
ai_handler = AIResponseHandler()

# Database connection
def get_db():
    return psycopg2.connect(
        dbname="celloxen_portal",
        user="celloxen_user",
        password="CelloxenSecure2025",
        host="localhost"
    )

# ==========================================
# PYDANTIC MODELS
# ==========================================

class StartSessionRequest(BaseModel):
    patient_id: int
    practitioner_id: int
    clinic_id: Optional[int] = None

class SendMessageRequest(BaseModel):
    session_token: str
    sender_type: str  # 'bot', 'patient', 'practitioner'
    sender_id: Optional[int] = None
    message_type: str  # 'text', 'question', 'instruction', etc.
    message_text: str
    question_id: Optional[str] = None
    answer_value: Optional[str] = None
    answer_score: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class UpdateSessionStageRequest(BaseModel):
    session_token: str
    stage: str
    progress_data: Optional[Dict[str, bool]] = None

class CaptureIrisImageRequest(BaseModel):
    session_token: str
    eye: str  # 'left' or 'right'
    image_base64: str
    quality_score: Optional[int] = None

# ==========================================
# SESSION MANAGEMENT ENDPOINTS
# ==========================================

@router.post("/chatbot/sessions/start")
async def start_chatbot_session(request: StartSessionRequest):
    """
    Start a new chatbot assessment session
    """
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Generate unique session token
        session_token = secrets.token_urlsafe(32)
        
        # Create new session
        cur.execute("""
            INSERT INTO chatbot_sessions (
                session_token, patient_id, practitioner_id, clinic_id,
                status, current_stage
            ) VALUES (%s, %s, %s, %s, 'active', 'introduction')
            RETURNING id, session_token, created_at
        """, (session_token, request.patient_id, request.practitioner_id, request.clinic_id))
        
        session = cur.fetchone()
        
        # Get patient info
        cur.execute("""
            SELECT first_name, last_name, email
            FROM patients
            WHERE id = %s
        """, (request.patient_id,))
        
        patient = cur.fetchone()
        
        # Create initial welcome message from bot
        welcome_message = f"""Hello {patient['first_name']}! Welcome to your comprehensive wellness assessment. !

I'm Cellie, your wellness assessment assistant. I'll be guiding you through today's evaluation.


Today's assessment includes:
1. Review your wellness questionnaire
2. Ask some follow-up questions
3. Capture iris images for analysis
4. Generate your comprehensive report

This will take about 30-45 minutes.

Are you ready to begin?"""
        
        cur.execute("""
            INSERT INTO chatbot_messages (
                session_id, sender_type, message_type, message_text
            ) VALUES (%s, 'bot', 'text', %s)
        """, (session['id'], welcome_message))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "session_id": session['id'],
            "session_token": session['session_token'],
            "patient": patient,
            "welcome_message": welcome_message
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/chatbot/sessions/{session_token}")
async def get_session(session_token: str):
    """
    Get session details and all messages
    """
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get session
        cur.execute("""
            SELECT s.*, 
                   p.first_name as patient_first_name,
                   p.last_name as patient_last_name,
                   u.username as practitioner_name
            FROM chatbot_sessions s
            JOIN patients p ON s.patient_id = p.id
            LEFT JOIN users u ON s.practitioner_id = u.id
            WHERE s.session_token = %s
        """, (session_token,))
        
        session = cur.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all messages
        cur.execute("""
            SELECT *
            FROM chatbot_messages
            WHERE session_id = %s
            ORDER BY created_at ASC
        """, (session['id'],))
        
        messages = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "session": dict(session),
            "messages": [dict(m) for m in messages]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==========================================
# MESSAGE ENDPOINTS
# ==========================================

@router.post("/chatbot/messages/send")
async def send_message(request: SendMessageRequest):
    """
    Send a message in the chatbot session with AI-powered responses
    """
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get session ID and context
        cur.execute("""
            SELECT s.id, s.current_stage, s.session_data, s.patient_id,
                   p.first_name, p.last_name, p.patient_number
            FROM chatbot_sessions s
            JOIN patients p ON s.patient_id = p.id
            WHERE s.session_token = %s
        """, (request.session_token,))
        
        session = cur.fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Insert user message
        cur.execute("""
            INSERT INTO chatbot_messages (
                session_id, sender_type, sender_id, message_type,
                message_text, question_id, answer_value, answer_score,
                metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, (
            session['id'],
            request.sender_type,
            request.sender_id,
            request.message_type,
            request.message_text,
            request.question_id,
            request.answer_value,
            request.answer_score,
            json.dumps(request.metadata) if request.metadata else None
        ))
        
        user_message = cur.fetchone()
        
        # Prepare context for AI
        session_context = {
            'current_stage': session.get('current_stage', 'introduction'),
            'session_data': session.get('session_data', {})
        }
        
        patient_context = {
            'first_name': session['first_name'],
            'last_name': session['last_name'],
            'patient_number': session['patient_number']
        }
        
        # Get AI-generated response
        ai_response = ai_handler.get_response(
            request.message_text,
            session_context,
            patient_context
        )
        
        bot_message_text = ai_response['message']
        next_stage = ai_response.get('next_stage')
        
        # Update session stage if AI suggests moving forward
        if next_stage:
            cur.execute("""
                UPDATE chatbot_sessions 
                SET current_stage = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (next_stage, session['id']))
        
        # Insert bot response
        cur.execute("""
            INSERT INTO chatbot_messages (
                session_id, sender_type, message_type, message_text
            ) VALUES (%s, %s, %s, %s)
            RETURNING id, created_at
        """, (session['id'], 'bot', 'text', bot_message_text))
        
        bot_message = cur.fetchone()
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "user_message": {
                "id": user_message['id'],
                "created_at": str(user_message['created_at'])
            },
            "bot_response": {
                "id": bot_message['id'],
                "message_text": bot_message_text,
                "sender_type": "bot",
                "created_at": str(bot_message['created_at']),
                "next_stage": next_stage
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chatbot/sessions/update-stage")
async def update_session_stage(request: UpdateSessionStageRequest):
    """
    Update the current stage of the session
    """
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Build update query based on progress data
        update_fields = ["current_stage = %s"]
        params = [request.stage]
        
        if request.progress_data:
            for key, value in request.progress_data.items():
                update_fields.append(f"{key} = %s")
                params.append(value)
        
        params.append(request.session_token)
        
        query = f"""
            UPDATE chatbot_sessions
            SET {', '.join(update_fields)}
            WHERE session_token = %s
        """
        
        cur.execute(query, params)
        conn.commit()
        cur.close()
        conn.close()
        
        return {"success": True, "stage": request.stage}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==========================================
# IRIDOLOGY CAPTURE ENDPOINTS
# ==========================================

@router.post("/chatbot/iridology/capture")
async def capture_iris_image(request: CaptureIrisImageRequest):
    """
    Capture and store iris image
    """
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get session
        cur.execute("""
            SELECT id FROM chatbot_sessions
            WHERE session_token = %s
        """, (request.session_token,))
        
        session = cur.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if capture session exists
        cur.execute("""
            SELECT id FROM iridology_capture_sessions
            WHERE chatbot_session_id = %s
        """, (session['id'],))
        
        capture_session = cur.fetchone()
        
        # Save image based on eye
        if request.eye == 'left':
            if capture_session:
                cur.execute("""
                    UPDATE iridology_capture_sessions
                    SET left_eye_image_base64 = %s,
                        left_eye_captured_at = CURRENT_TIMESTAMP,
                        left_eye_quality_score = %s
                    WHERE id = %s
                """, (request.image_base64, request.quality_score, capture_session['id']))
            else:
                cur.execute("""
                    INSERT INTO iridology_capture_sessions (
                        chatbot_session_id, left_eye_image_base64,
                        left_eye_quality_score
                    ) VALUES (%s, %s, %s)
                    RETURNING id
                """, (session['id'], request.image_base64, request.quality_score))
                capture_session = cur.fetchone()
            
            # Update session progress
            cur.execute("""
                UPDATE chatbot_sessions
                SET left_eye_captured = TRUE,
                    current_stage = 'capture_right_eye'
                WHERE id = %s
            """, (session['id'],))
            
        else:  # right eye
            cur.execute("""
                UPDATE iridology_capture_sessions
                SET right_eye_image_base64 = %s,
                    right_eye_captured_at = CURRENT_TIMESTAMP,
                    right_eye_quality_score = %s
                WHERE chatbot_session_id = %s
            """, (request.image_base64, request.quality_score, session['id']))
            
            # Update session progress
            cur.execute("""
                UPDATE chatbot_sessions
                SET right_eye_captured = TRUE,
                    current_stage = 'ai_analysis'
                WHERE id = %s
            """, (session['id'],))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "eye": request.eye,
            "captured": True,
            "next_stage": "capture_right_eye" if request.eye == "left" else "ai_analysis"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/chatbot/iridology/status/{session_token}")
async def get_iridology_status(session_token: str):
    """
    Get current iridology capture status
    """
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("""
            SELECT ics.*
            FROM iridology_capture_sessions ics
            JOIN chatbot_sessions cs ON ics.chatbot_session_id = cs.id
            WHERE cs.session_token = %s
        """, (session_token,))
        
        status = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "left_eye_captured": status['left_eye_captured_at'] is not None if status else False,
            "right_eye_captured": status['right_eye_captured_at'] is not None if status else False,
            "ai_analysis_completed": status['ai_analysis_completed_at'] is not None if status else False
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==========================================
# COMPLETE SESSION
# ==========================================

@router.post("/chatbot/sessions/{session_token}/complete")
async def complete_session(session_token: str):
    """
    Mark session as completed
    """
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE chatbot_sessions
            SET status = 'completed',
                completed_at = CURRENT_TIMESTAMP,
                duration_minutes = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - started_at)) / 60
            WHERE session_token = %s
        """, (session_token,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"success": True, "status": "completed"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

