from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_clinics():
    return {"message": "clinics endpoint"}
