from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncpg
import bcrypt
import os
from ....core.database import get_db
from ....core.security import verify_password, create_access_token, verify_token
from ....schemas.user import UserLogin, Token

router = APIRouter()
security = HTTPBearer()

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "celloxen_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "celloxen_portal")

@router.post("/login")
async def login(user_credentials: UserLogin):
    """
    Login endpoint with real authentication
    """
    if not DB_PASSWORD:
        raise HTTPException(status_code=500, detail="Database configuration error")

    try:
        # Connect directly to database
        conn = await asyncpg.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        # Get user from database
        user = await conn.fetchrow(
            "SELECT id, email, full_name, role, status, password_hash FROM users WHERE email = $1",
            user_credentials.email
        )

        if not user:
            await conn.close()
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Verify password using bcrypt
        if not user['password_hash'] or not bcrypt.checkpw(
            user_credentials.password.encode('utf-8'),
            user['password_hash'].encode('utf-8')
        ):
            await conn.close()
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create access token
        access_token = create_access_token(subject=user['email'])

        await conn.close()

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user['full_name'],
                "role": user['role'],
                "status": user['status']
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        # Log error internally but don't expose details
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication service error")

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current authenticated user endpoint
    """
    if not DB_PASSWORD:
        raise HTTPException(status_code=500, detail="Database configuration error")

    try:
        # Verify the token
        username = verify_token(credentials.credentials)
        if not username:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Get user from database
        conn = await asyncpg.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        user = await conn.fetchrow(
            "SELECT id, email, full_name, role, status FROM users WHERE email = $1",
            username
        )
        await conn.close()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user['id'],
            "email": user['email'],
            "full_name": user['full_name'],
            "role": user['role'],
            "status": user['status']
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get current user error: {str(e)}")
        raise HTTPException(status_code=500, detail="Service error")
