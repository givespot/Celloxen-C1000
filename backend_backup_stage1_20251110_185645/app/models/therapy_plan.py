from sqlalchemy import Column, BigInteger, String, Enum, ForeignKey, DateTime, Date, Integer, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class TherapyPlanStatus(str, enum.Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TherapyDomain(str, enum.Enum):
    DIABETICS = "diabetics"
    CHRONIC_PAIN = "chronic_pain"
    ANXIETY_STRESS = "anxiety_stress"
    ENERGY_VITALITY = "energy_vitality"

class TherapyPriority(str, enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUPPLEMENTARY = "supplementary"

class TherapyPlan(Base):
    __tablename__ = "therapy_plans"
    
    id = Column(BigInteger, primary_key=True, index=True)
    plan_number = Column(String(50), unique=True, nullable=False)
    clinic_id = Column(BigInteger, ForeignKey("clinics.id"), nullable=False)
    patient_id = Column(BigInteger, ForeignKey("patients.id"), nullable=False)
    assessment_id = Column(BigInteger, ForeignKey("assessments.id"), nullable=False)
    recommended_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(TherapyPlanStatus), default=TherapyPlanStatus.PENDING_APPROVAL)
    patient_consent = Column(Boolean, default=False)
    consent_date = Column(Date, nullable=True)
    consent_signature = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    notes = Column(Text, nullable=True)
    
    @property
    def is_active(self) -> bool:
        return self.status in [TherapyPlanStatus.APPROVED, TherapyPlanStatus.IN_PROGRESS]
    
    @property
    def has_patient_consent(self) -> bool:
        return self.patient_consent and self.consent_date is not None

class TherapyPlanItem(Base):
    __tablename__ = "therapy_plan_items"
    
    id = Column(BigInteger, primary_key=True, index=True)
    therapy_plan_id = Column(BigInteger, ForeignKey("therapy_plans.id"), nullable=False)
    therapy_code = Column(String(20), nullable=False)
    therapy_name = Column(String(255), nullable=False)
    therapy_description = Column(Text, nullable=True)
    recommended_sessions = Column(Integer, nullable=False)
    session_duration_minutes = Column(Integer, default=60)
    rationale = Column(Text, nullable=True)
    target_domain = Column(Enum(TherapyDomain), nullable=True)
    priority = Column(Enum(TherapyPriority), default=TherapyPriority.PRIMARY)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
