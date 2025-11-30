from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from ..models.patient import Gender, PatientStatus

# Base Patient schema
class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: Optional[Gender] = None
    email: EmailStr
    mobile_phone: str = Field(..., min_length=1, max_length=50)
    home_phone: Optional[str] = Field(None, max_length=50)
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    county: Optional[str] = Field(None, max_length=100)
    postcode: str = Field(..., min_length=1, max_length=20)
    country: str = Field(default="United Kingdom", max_length=100)

# Schema for creating a patient
class PatientCreate(PatientBase):
    clinic_id: int
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    nhs_number: Optional[str] = Field(None, max_length=20)
    gp_name: Optional[str] = Field(None, max_length=255)
    gp_practice: Optional[str] = Field(None, max_length=255)
    gp_address: Optional[str] = None
    gp_phone: Optional[str] = Field(None, max_length=50)
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    allergies: Optional[str] = None

# Schema for updating a patient
class PatientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    email: Optional[EmailStr] = None
    mobile_phone: Optional[str] = Field(None, min_length=1, max_length=50)
    home_phone: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    county: Optional[str] = Field(None, max_length=100)
    postcode: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    nhs_number: Optional[str] = Field(None, max_length=20)
    gp_name: Optional[str] = Field(None, max_length=255)
    gp_practice: Optional[str] = Field(None, max_length=255)
    gp_address: Optional[str] = None
    gp_phone: Optional[str] = Field(None, max_length=50)
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    allergies: Optional[str] = None
    status: Optional[PatientStatus] = None
    portal_access: Optional[bool] = None

# Schema for patient response
class PatientResponse(PatientBase):
    id: int
    patient_number: str
    clinic_id: int
    emergency_contact_name: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    nhs_number: Optional[str] = None
    gp_name: Optional[str] = None
    gp_practice: Optional[str] = None
    gp_address: Optional[str] = None
    gp_phone: Optional[str] = None
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    allergies: Optional[str] = None
    portal_access: bool
    portal_activated_at: Optional[datetime] = None
    status: PatientStatus
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    full_name: str
    is_active: bool
    has_portal_access: bool
    full_address: str
    
    class Config:
        from_attributes = True

# Schema for patient list (minimal info)
class PatientSummary(BaseModel):
    id: int
    patient_number: str
    first_name: str
    last_name: str
    email: str
    mobile_phone: str
    status: PatientStatus
    portal_access: bool
    
    class Config:
        from_attributes = True
