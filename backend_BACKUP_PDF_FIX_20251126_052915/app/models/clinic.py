from sqlalchemy import Column, BigInteger, String, Enum, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class ClinicStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class SubscriptionStatus(str, enum.Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class Clinic(Base):
    __tablename__ = "clinics"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    county = Column(String(100), nullable=True)
    postcode = Column(String(20), nullable=False)
    country = Column(String(100), default="United Kingdom")
    celloxen_device = Column(String(50), nullable=True)
    device_serial_number = Column(String(100), nullable=True)
    status = Column(Enum(ClinicStatus), default=ClinicStatus.ACTIVE)
    subscription_status = Column(Enum(SubscriptionStatus), nullable=True)
    subscription_expires_at = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    @property
    def is_active(self) -> bool:
        return self.status == ClinicStatus.ACTIVE
    
    @property
    def subscription_active(self) -> bool:
        return self.subscription_status == SubscriptionStatus.ACTIVE
    
    @property
    def full_address(self) -> str:
        address_parts = [self.address_line1]
        if self.address_line2:
            address_parts.append(self.address_line2)
        address_parts.extend([self.city, self.postcode])
        if self.county:
            address_parts.insert(-1, self.county)
        return ", ".join(address_parts)
