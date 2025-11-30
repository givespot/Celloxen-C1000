from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_notifications():
    return {"message": "notifications endpoint"}
