from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import bcrypt
from datetime import datetime, timedelta

# JWT Configuration
SECRET_KEY = "celloxen-super-admin-secret-key-change-in-production-2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer()

def verify_super_admin_password(plain_password: str, hashed_password: str) -> bool:
    """Verify super admin password"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def create_super_admin_token(super_admin_id: int, email: str) -> str:
    """Create JWT token for super admin"""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = {
        "super_admin_id": super_admin_id,
        "email": email,
        "type": "super_admin",
        "exp": expire
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_super_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify super admin JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "super_admin":
            raise HTTPException(status_code=403, detail="Not a super admin token")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
