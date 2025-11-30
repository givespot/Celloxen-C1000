from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from .config import settings
from .database import get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handler
security = HTTPBearer()


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    Create JWT access token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


def verify_token(token: str) -> Optional[str]:
    """
    Verify JWT token and return subject
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user
    """
    from ..models.user import User
    from sqlalchemy import select
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        username = verify_token(credentials.credentials)
        if username is None:
            raise credentials_exception
            
        # Get user from database
        result = await db.execute(
            select(User).where(User.email == username)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
            
        return user
        
    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Get current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_super_admin(
    current_user = Depends(get_current_active_user)
):
    """
    Require super admin role
    """
    if current_user.role != settings.USER_ROLES["SUPER_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


async def get_current_clinic_user(
    current_user = Depends(get_current_active_user)
):
    """
    Require clinic user role
    """
    allowed_roles = [
        settings.USER_ROLES["SUPER_ADMIN"],
        settings.USER_ROLES["CLINIC_USER"]
    ]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clinic access required"
        )
    return current_user


async def get_current_patient(
    current_user = Depends(get_current_active_user)
):
    """
    Require patient role
    """
    if current_user.role != settings.USER_ROLES["PATIENT"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient access required"
        )
    return current_user


def check_clinic_access(user, clinic_id: int) -> bool:
    """
    Check if user has access to specific clinic
    """
    # Super admins have access to all clinics
    if user.role == settings.USER_ROLES["SUPER_ADMIN"]:
        return True
    
    # Clinic users only have access to their clinic
    if hasattr(user, 'clinic_id') and user.clinic_id == clinic_id:
        return True
    
    return False


async def require_clinic_access(
    clinic_id: int,
    current_user = Depends(get_current_clinic_user)
):
    """
    Require access to specific clinic
    """
    if not check_clinic_access(current_user, clinic_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this clinic"
        )
    return current_user
