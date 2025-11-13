from fastapi import APIRouter
from .endpoints import auth, users, clinics, patients, appointments, assessments, therapy_plans, therapy_sessions, notifications

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(clinics.router, prefix="/clinics", tags=["Clinics"])
api_router.include_router(patients.router, prefix="/patients", tags=["Patients"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(therapy_plans.router, prefix="/therapy-plans", tags=["Therapy Plans"])
api_router.include_router(therapy_sessions.router, prefix="/therapy-sessions", tags=["Therapy Sessions"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
