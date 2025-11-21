from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from ..models.therapy_plan import TherapyPlanStatus, TherapyDomain, TherapyPriority

# Therapy Plan Item schemas
class TherapyPlanItemBase(BaseModel):
    therapy_code: str = Field(..., max_length=20)
    therapy_name: str = Field(..., max_length=255)
    therapy_description: Optional[str] = None
    recommended_sessions: int = Field(..., ge=1, le=50)
    session_duration_minutes: int = Field(default=60, ge=15, le=240)
    rationale: Optional[str] = None
    target_domain: Optional[TherapyDomain] = None
    priority: TherapyPriority = TherapyPriority.PRIMARY

class TherapyPlanItemCreate(TherapyPlanItemBase):
    therapy_plan_id: int

class TherapyPlanItemResponse(TherapyPlanItemBase):
    id: int
    therapy_plan_id: int
    created_at: datetime
    
    # Computed properties
    sessions_completed: int
    sessions_remaining: int
    completion_percentage: float
    
    class Config:
        from_attributes = True

# Base Therapy Plan schema
class TherapyPlanBase(BaseModel):
    notes: Optional[str] = None

# Schema for creating a therapy plan
class TherapyPlanCreate(TherapyPlanBase):
    clinic_id: int
    patient_id: int
    assessment_id: int
    recommended_by: int  # Practitioner user ID
    therapy_items: List[TherapyPlanItemBase] = []

# Schema for updating a therapy plan
class TherapyPlanUpdate(BaseModel):
    status: Optional[TherapyPlanStatus] = None
    patient_consent: Optional[bool] = None
    consent_date: Optional[date] = None
    consent_signature: Optional[str] = None
    notes: Optional[str] = None

# Schema for therapy plan response
class TherapyPlanResponse(TherapyPlanBase):
    id: int
    plan_number: str
    clinic_id: int
    patient_id: int
    assessment_id: int
    recommended_by: int
    status: TherapyPlanStatus
    patient_consent: bool
    consent_date: Optional[date] = None
    consent_signature: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_active: bool
    has_patient_consent: bool
    
    # Relationships
    therapy_items: List[TherapyPlanItemResponse] = []
    
    class Config:
        from_attributes = True

# Schema for therapy plan summary
class TherapyPlanSummary(BaseModel):
    id: int
    plan_number: str
    status: TherapyPlanStatus
    patient_consent: bool
    created_at: datetime
    total_therapies: int
    total_sessions: int
    completed_sessions: int
    
    class Config:
        from_attributes = True

# Schema for patient consent
class PatientConsentUpdate(BaseModel):
    patient_consent: bool
    consent_signature: Optional[str] = None

# Schema for therapy recommendation
class TherapyRecommendation(BaseModel):
    therapy_code: str
    therapy_name: str
    recommended_sessions: int
    rationale: str
    target_domain: TherapyDomain
    priority: TherapyPriority
    confidence_score: float  # AI-generated confidence in recommendation
    
    class Config:
        from_attributes = True
