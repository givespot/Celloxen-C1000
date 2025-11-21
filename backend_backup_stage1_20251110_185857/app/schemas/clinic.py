from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from ..models.clinic import ClinicStatus, SubscriptionStatus

# Base Clinic schema
class ClinicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=1, max_length=50)
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    county: Optional[str] = Field(None, max_length=100)
    postcode: str = Field(..., min_length=1, max_length=20)
    country: str = Field(default="United Kingdom", max_length=100)
    celloxen_device: Optional[str] = Field(None, max_length=50)
    device_serial_number: Optional[str] = Field(None, max_length=100)

# Schema for creating a clinic
class ClinicCreate(ClinicBase):
    subscription_status: Optional[SubscriptionStatus] = SubscriptionStatus.TRIAL
    subscription_expires_at: Optional[date] = None

# Schema for updating a clinic
class ClinicUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=1, max_length=50)
    address_line1: Optional[str] = Field(None, min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    county: Optional[str] = Field(None, max_length=100)
    postcode: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    celloxen_device: Optional[str] = Field(None, max_length=50)
    device_serial_number: Optional[str] = Field(None, max_length=100)
    status: Optional[ClinicStatus] = None
    subscription_status: Optional[SubscriptionStatus] = None
    subscription_expires_at: Optional[date] = None

# Schema for clinic response
class ClinicResponse(ClinicBase):
    id: int
    status: ClinicStatus
    subscription_status: Optional[SubscriptionStatus] = None
    subscription_expires_at: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_active: bool
    subscription_active: bool
    full_address: str
    
    class Config:
        from_attributes = True

# Schema for clinic list (minimal info)
class ClinicSummary(BaseModel):
    id: int
    name: str
    city: str
    postcode: str
    status: ClinicStatus
    subscription_status: Optional[SubscriptionStatus] = None
    
    class Config:
        from_attributes = True
