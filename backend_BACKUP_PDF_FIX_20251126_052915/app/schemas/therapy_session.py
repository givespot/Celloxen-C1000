from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date, time
from decimal import Decimal
from ..models.therapy_session import TherapySessionStatus, PaymentStatus

# Base Therapy Session schema
class TherapySessionBase(BaseModel):
    scheduled_date: date
    scheduled_time: time
    duration_minutes: int = Field(default=60, ge=15, le=240)
    therapist_notes: Optional[str] = None
    patient_feedback: Optional[str] = None
    any_concerns: bool = False
    concern_details: Optional[str] = None

# Schema for creating a therapy session
class TherapySessionCreate(TherapySessionBase):
    therapy_plan_item_id: int
    clinic_id: int
    patient_id: int
    session_sequence: int = Field(..., ge=1)
    total_sessions: int = Field(..., ge=1)
    therapist_id: Optional[int] = None
    therapy_settings: Optional[Dict[str, Any]] = None
    payment_amount: Optional[Decimal] = None

# Schema for updating a therapy session
class TherapySessionUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=240)
    therapist_id: Optional[int] = None
    status: Optional[TherapySessionStatus] = None
    therapy_settings: Optional[Dict[str, Any]] = None
    therapist_notes: Optional[str] = None
    patient_feedback: Optional[str] = None
    any_concerns: Optional[bool] = None
    concern_details: Optional[str] = None
    payment_status: Optional[PaymentStatus] = None
    payment_amount: Optional[Decimal] = None

# Schema for session check-in
class SessionCheckIn(BaseModel):
    checked_in_at: datetime
    therapist_id: Optional[int] = None
    therapy_settings: Optional[Dict[str, Any]] = None

# Schema for session start
class SessionStart(BaseModel):
    started_at: datetime
    therapy_settings: Optional[Dict[str, Any]] = None

# Schema for session completion
class SessionComplete(BaseModel):
    completed_at: datetime
    therapist_notes: Optional[str] = None
    patient_feedback: Optional[str] = None
    any_concerns: bool = False
    concern_details: Optional[str] = None
    therapy_settings: Optional[Dict[str, Any]] = None

# Schema for therapy session response
class TherapySessionResponse(TherapySessionBase):
    id: int
    session_number: str
    therapy_plan_item_id: int
    clinic_id: int
    patient_id: int
    session_sequence: int
    total_sessions: int
    therapist_id: Optional[int] = None
    status: TherapySessionStatus
    checked_in_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    therapy_settings: Optional[Dict[str, Any]] = None
    payment_status: PaymentStatus
    payment_amount: Optional[Decimal] = None
    reminder_sent_48h: bool
    reminder_sent_24h: bool
    reminder_sent_2h: bool
    completion_notification_sent: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    # Computed properties
    is_completed: bool
    can_be_started: bool
    can_be_cancelled: bool
    session_progress: str
    datetime_str: str
    
    class Config:
        from_attributes = True

# Schema for therapy session summary
class TherapySessionSummary(BaseModel):
    id: int
    session_number: str
    scheduled_date: date
    scheduled_time: time
    session_sequence: int
    total_sessions: int
    status: TherapySessionStatus
    payment_status: PaymentStatus
    
    class Config:
        from_attributes = True

# Schema for session calendar view
class SessionCalendar(BaseModel):
    id: int
    session_number: str
    title: str  # Generated from therapy and patient
    start: datetime  # Combined date and time
    end: datetime    # Start + duration
    status: TherapySessionStatus
    patient_name: str
    therapist_name: Optional[str] = None
    therapy_name: str
    session_progress: str
    
    class Config:
        from_attributes = True

# Schema for therapy device settings
class TherapyDeviceSettings(BaseModel):
    device_code: str
    intensity_level: int = Field(..., ge=1, le=10)
    frequency: Optional[float] = None
    duration_minutes: int = Field(..., ge=5, le=120)
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    custom_settings: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
