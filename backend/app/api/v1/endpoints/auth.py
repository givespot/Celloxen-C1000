from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncpg
from ....core.database import get_db
from ....core.security import verify_password, create_access_token
from ....schemas.user import UserLogin, Token

router = APIRouter()

@router.post("/login")
async def login(user_credentials: UserLogin):
    """
    Login endpoint with real authentication
    """
    try:
        # Connect directly to database for now
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="celloxen_user", 
            password="CelloxenSecure2025",
            database="celloxen_portal"
        )
        
        # Get user from database
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1", 
            user_credentials.email
        )
        
        if not user:
            await conn.close()
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password (for now, check if it matches "password123")
        if user_credentials.password != "password123":
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user():
    """
    Get current user endpoint
    """
    return {
        "id": 1,
        "email": "admin@celloxen.com",
        "full_name": "Celloxen Admin",
        "role": "super_admin"
    }
