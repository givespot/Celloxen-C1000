from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_assessments():
    return {"message": "assessments endpoint"}
