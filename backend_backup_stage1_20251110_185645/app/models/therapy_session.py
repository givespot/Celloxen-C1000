from sqlalchemy import Column, BigInteger, String, Enum, ForeignKey, DateTime, Date, Time, Integer, Boolean, Text, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class TherapySessionStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    WAIVED = "waived"

class TherapySession(Base):
    __tablename__ = "therapy_sessions"
    
    id = Column(BigInteger, primary_key=True, index=True)
    session_number = Column(String(50), unique=True, nullable=False)
    therapy_plan_item_id = Column(BigInteger, ForeignKey("therapy_plan_items.id"), nullable=False)
    clinic_id = Column(BigInteger, ForeignKey("clinics.id"), nullable=False)
    patient_id = Column(BigInteger, ForeignKey("patients.id"), nullable=False)
    session_sequence = Column(Integer, nullable=False)
    total_sessions = Column(Integer, nullable=False)
    scheduled_date = Column(Date, nullable=False)
    scheduled_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=60)
    therapist_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(TherapySessionStatus), default=TherapySessionStatus.SCHEDULED)
    checked_in_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    therapy_settings = Column(JSON, nullable=True)
    therapist_notes = Column(Text, nullable=True)
    patient_feedback = Column(Text, nullable=True)
    any_concerns = Column(Boolean, default=False)
    concern_details = Column(Text, nullable=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_amount = Column(DECIMAL(10,2), nullable=True)
    reminder_sent_48h = Column(Boolean, default=False)
    reminder_sent_24h = Column(Boolean, default=False)
    reminder_sent_2h = Column(Boolean, default=False)
    completion_notification_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    
    @property
    def is_completed(self) -> bool:
        return self.status == TherapySessionStatus.COMPLETED
    
    @property
    def can_be_started(self) -> bool:
        return self.status == TherapySessionStatus.CHECKED_IN
    
    @property
    def can_be_cancelled(self) -> bool:
        return self.status in [TherapySessionStatus.SCHEDULED, TherapySessionStatus.CHECKED_IN]
    
    @property
    def session_progress(self) -> str:
        return f"{self.session_sequence} of {self.total_sessions}"
