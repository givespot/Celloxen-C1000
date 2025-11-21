from sqlalchemy import Column, BigInteger, String, Enum, ForeignKey, DateTime, Date, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class PatientStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_HOLD = "on_hold"

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(BigInteger, primary_key=True, index=True)
    patient_number = Column(String(50), unique=True, nullable=False)
    clinic_id = Column(BigInteger, ForeignKey("clinics.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    mobile_phone = Column(String(50), nullable=False)
    home_phone = Column(String(50), nullable=True)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    county = Column(String(100), nullable=True)
    postcode = Column(String(20), nullable=False)
    country = Column(String(100), default="United Kingdom")
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_relationship = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(50), nullable=True)
    nhs_number = Column(String(20), nullable=True)
    gp_name = Column(String(255), nullable=True)
    gp_practice = Column(String(255), nullable=True)
    gp_address = Column(Text, nullable=True)
    gp_phone = Column(String(50), nullable=True)
    medical_history = Column(Text, nullable=True)
    current_medications = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    portal_access = Column(Boolean, default=False)
    portal_activated_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(PatientStatus), default=PatientStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_active(self) -> bool:
        return self.status == PatientStatus.ACTIVE
    
    @property
    def has_portal_access(self) -> bool:
        return self.portal_access and self.portal_activated_at is not None
