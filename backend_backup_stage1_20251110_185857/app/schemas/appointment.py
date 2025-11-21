from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, time
from ..models.appointment import AppointmentType, AppointmentStatus

# Base Appointment schema
class AppointmentBase(BaseModel):
    appointment_type: AppointmentType
    appointment_date: date
    appointment_time: time
    duration_minutes: int = Field(default=60, ge=15, le=480)
    booking_notes: Optional[str] = None

# Schema for creating an appointment
class AppointmentCreate(AppointmentBase):
    clinic_id: int
    patient_id: int
    practitioner_id: Optional[int] = None
    therapist_id: Optional[int] = None

# Schema for updating an appointment
class AppointmentUpdate(BaseModel):
    appointment_type: Optional[AppointmentType] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    practitioner_id: Optional[int] = None
    therapist_id: Optional[int] = None
    status: Optional[AppointmentStatus] = None
    booking_notes: Optional[str] = None
    cancellation_reason: Optional[str] = None

# Schema for appointment response
class AppointmentResponse(AppointmentBase):
    id: int
    appointment_number: str
    clinic_id: int
    patient_id: int
    practitioner_id: Optional[int] = None
    therapist_id: Optional[int] = None
    status: AppointmentStatus
    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[int] = None
    reminder_sent_24h: bool
    reminder_sent_2h: bool
    confirmation_sent: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    # Computed properties
    is_active: bool
    can_be_cancelled: bool
    datetime_str: str
    
    class Config:
        from_attributes = True

# Schema for appointment list (minimal info)
class AppointmentSummary(BaseModel):
    id: int
    appointment_number: str
    appointment_type: AppointmentType
    appointment_date: date
    appointment_time: time
    duration_minutes: int
    patient_id: int
    status: AppointmentStatus
    
    class Config:
        from_attributes = True

# Schema for appointment calendar view
class AppointmentCalendar(BaseModel):
    id: int
    appointment_number: str
    title: str  # Generated from type and patient name
    start: datetime  # Combined date and time
    end: datetime    # Start + duration
    status: AppointmentStatus
    patient_name: str
    practitioner_name: Optional[str] = None
    therapist_name: Optional[str] = None
    
    class Config:
        from_attributes = True
