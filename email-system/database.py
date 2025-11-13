"""
Database utilities for email system
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import secrets
import string
from config import *


def get_db():
    """Get database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def log_email(patient_id, email_type, sent_to_email, subject, status, error_message=None):
    """Log email to database"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO email_logs 
            (patient_id, email_type, sent_to_email, subject, status, sent_at, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (patient_id, email_type, sent_to_email, subject, status, datetime.now(), error_message))
        
        log_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return log_id
        
    except Exception as e:
        print(f"Email logging failed: {e}")
        return None


def create_patient_invitation(first_name, last_name, email, phone=None):
    """Create patient record with invitation token"""
    
    # Generate secure token
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(32))
    expires_at = datetime.now() + timedelta(days=7)
    
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO patients 
            (first_name, last_name, email, phone, registration_token, token_expires_at, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'INVITED')
            RETURNING id, registration_token, token_expires_at
        """, (first_name, last_name, email, phone, token, expires_at))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'patient_id': result['id'],
            'registration_token': result['registration_token'],
            'expires_at': result['token_expires_at'].isoformat()
        }
        
    except Exception as e:
        print(f"Failed to create patient invitation: {e}")
        raise e


def validate_token(token):
    """Validate registration token"""
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT id, first_name, last_name, email, token_expires_at, status
            FROM patients
            WHERE registration_token = %s
        """, (token,))
        
        patient = cur.fetchone()
        cur.close()
        conn.close()
        
        if not patient:
            return None
        
        # Check if expired
        if patient['token_expires_at'] < datetime.now():
            return None
        
        # Check if already used
        if patient['status'] not in ['INVITED', 'PRE_REGISTERED']:
            return None
        
        return dict(patient)
        
    except Exception as e:
        print(f"Token validation failed: {e}")
        return None
