from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_therapy_plans():
    return {"message": "therapy_plans endpoint"}
