from sqlalchemy import Column, BigInteger, String, Enum, ForeignKey, DateTime, Date, Time, Integer, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class AppointmentType(str, enum.Enum):
    INITIAL_ASSESSMENT = "initial_assessment"
    FOLLOW_UP = "follow_up"
    THERAPY_SESSION = "therapy_session"
    REVIEW = "review"
    CONSULTATION = "consultation"

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(BigInteger, primary_key=True, index=True)
    appointment_number = Column(String(50), unique=True, nullable=False)
    clinic_id = Column(BigInteger, ForeignKey("clinics.id"), nullable=False)
    patient_id = Column(BigInteger, ForeignKey("patients.id"), nullable=False)
    appointment_type = Column(Enum(AppointmentType), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=60)
    practitioner_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    therapist_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    booking_notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    reminder_sent_24h = Column(Boolean, default=False)
    reminder_sent_2h = Column(Boolean, default=False)
    confirmation_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    
    @property
    def is_active(self) -> bool:
        return self.status not in [AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]
    
    @property
    def can_be_cancelled(self) -> bool:
        return self.status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
