"""
Pydantic Models for CellOxen Health Portal
This file defines all data structures and automatically validates/converts types
MATCHES ACTUAL DATABASE SCHEMA - COMPLETE VERSION
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import date, time, datetime
from enum import Enum
from decimal import Decimal

# ============================================================================
# ENUMS - Match database exactly
# ============================================================================

class AppointmentType(str, Enum):
    INITIAL_ASSESSMENT = "INITIAL_ASSESSMENT"
    FOLLOW_UP = "FOLLOW_UP"
    THERAPY_SESSION = "THERAPY_SESSION"
    REVIEW = "REVIEW"
    CONSULTATION = "CONSULTATION"

class AppointmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
    RESCHEDULED = "RESCHEDULED"

class PatientStatus(str, Enum):
    ACTIVE = "active"
    INVITED = "invited"
    INACTIVE = "inactive"

class TherapyPlanStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class TherapySessionStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    CHECKED_IN = "CHECKED_IN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    WAIVED = "WAIVED"

# ============================================================================
# APPOINTMENT MODELS
# ============================================================================

class AppointmentCreate(BaseModel):
    """Model for creating a new appointment"""
    patient_id: int
    clinic_id: int = 1
    appointment_type: str  # Will be converted to enum
    appointment_date: str  # Will be parsed to date
    appointment_time: str  # Will be parsed to time
    duration_minutes: int = 60
    practitioner_id: Optional[int] = None
    booking_notes: Optional[str] = None
    
    @validator('appointment_type')
    def validate_appointment_type(cls, v):
        """Convert frontend format to database enum format"""
        return v.upper().replace(" ", "_")
    
    @validator('patient_id', 'clinic_id', 'practitioner_id')
    def convert_to_int(cls, v):
        """Ensure IDs are integers"""
        if v is None:
            return None
        return int(v) if isinstance(v, str) else v

# ============================================================================
# PATIENT MODELS
# ============================================================================

class PatientCreate(BaseModel):
    """Model for creating a new patient"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    mobile_phone: str = Field(..., min_length=10, max_length=50)
    date_of_birth: str  # Will be parsed to date
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    insurance_details: Optional[str] = None
    notes: Optional[str] = None
    clinic_id: int = 1
    
    @validator('clinic_id')
    def convert_clinic_id(cls, v):
        return int(v) if isinstance(v, str) else v

class PatientUpdate(BaseModel):
    """Model for updating a patient"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile_phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    insurance_details: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[PatientStatus] = None

# ============================================================================
# ASSESSMENT MODELS
# ============================================================================

class AssessmentResponse(BaseModel):
    """Model for a single assessment response"""
    question_id: int
    question_text: str
    answer: Any  # Can be string, int, bool, etc.
    score: Optional[int] = None
    domain: Optional[str] = None

class AssessmentCreate(BaseModel):
    """Model for creating a comprehensive assessment"""
    patient_id: int
    clinic_id: int = 1
    practitioner_id: Optional[int] = None
    responses: List[Dict[str, Any]]  # List of question responses
    wellness_scores: Optional[Dict[str, Any]] = None
    iridology_data: Optional[Dict[str, Any]] = None
    contraindications: Optional[List[str]] = None
    recommendations: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('patient_id', 'clinic_id', 'practitioner_id')
    def convert_to_int(cls, v):
        if v is None:
            return None
        return int(v) if isinstance(v, str) else v

class AssessmentUpdate(BaseModel):
    """Model for updating an assessment"""
    wellness_scores: Optional[Dict[str, Any]] = None
    recommendations: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

# ============================================================================
# THERAPY PLAN MODELS
# ============================================================================

class TherapyPlanCreate(BaseModel):
    """Model for creating a therapy plan"""
    patient_id: int
    assessment_id: int
    clinic_id: int = 1
    recommended_by: int  # User ID of practitioner
    patient_consent: bool = False
    consent_date: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('patient_id', 'assessment_id', 'clinic_id', 'recommended_by')
    def convert_to_int(cls, v):
        if v is None:
            return None
        return int(v) if isinstance(v, str) else v

class TherapyPlanUpdate(BaseModel):
    """Model for updating a therapy plan"""
    status: Optional[TherapyPlanStatus] = None
    patient_consent: Optional[bool] = None
    consent_date: Optional[str] = None
    consent_signature: Optional[str] = None
    notes: Optional[str] = None

# ============================================================================
# THERAPY SESSION MODELS
# ============================================================================

class TherapySessionCreate(BaseModel):
    """Model for creating a therapy session"""
    therapy_plan_item_id: int
    clinic_id: int
    patient_id: int
    session_sequence: int
    total_sessions: int
    scheduled_date: str  # Will be parsed to date
    scheduled_time: str  # Will be parsed to time
    duration_minutes: int = 60
    therapist_id: Optional[int] = None
    
    @validator('therapy_plan_item_id', 'clinic_id', 'patient_id', 'therapist_id')
    def convert_to_int(cls, v):
        if v is None:
            return None
        return int(v) if isinstance(v, str) else v

class TherapySessionUpdate(BaseModel):
    """Model for updating a therapy session"""
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    therapist_id: Optional[int] = None
    status: Optional[TherapySessionStatus] = None
    therapy_settings: Optional[Dict[str, Any]] = None
    therapist_notes: Optional[str] = None
    patient_feedback: Optional[str] = None
    any_concerns: Optional[bool] = None
    concern_details: Optional[str] = None
    payment_status: Optional[PaymentStatus] = None
    payment_amount: Optional[Decimal] = None

class TherapySessionCheckIn(BaseModel):
    """Model for checking in a patient for a session"""
    session_id: int
    
    @validator('session_id')
    def convert_to_int(cls, v):
        return int(v) if isinstance(v, str) else v

class TherapySessionComplete(BaseModel):
    """Model for completing a therapy session"""
    session_id: int
    therapist_notes: Optional[str] = None
    patient_feedback: Optional[str] = None
    any_concerns: bool = False
    concern_details: Optional[str] = None
    therapy_settings: Optional[Dict[str, Any]] = None
    
    @validator('session_id')
    def convert_to_int(cls, v):
        return int(v) if isinstance(v, str) else v

