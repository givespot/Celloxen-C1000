from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from ..models.user import UserRole, UserStatus

# Base User schema
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole
    clinic_id: Optional[int] = None

# Schema for creating a user
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

# Schema for updating a user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[UserRole] = None
    clinic_id: Optional[int] = None
    status: Optional[UserStatus] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)

# Schema for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"

# Schema for user response
class UserResponse(UserBase):
    id: int
    status: UserStatus
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_active: bool
    is_super_admin: bool
    is_clinic_user: bool
    is_patient: bool
    
    class Config:
        from_attributes = True

# Update forward reference
Token.model_rebuild()
