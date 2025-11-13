# Import all models here for easy access
from .user import User
from .clinic import Clinic
from .patient import Patient
from .appointment import Appointment
from .assessment import Assessment, AssessmentQuestion, AssessmentAnswer
from .therapy_plan import TherapyPlan, TherapyPlanItem
from .therapy_session import TherapySession
from .notification import Notification
from .audit_log import AuditLog

# Export all models
__all__ = [
    "User",
    "Clinic", 
    "Patient",
    "Appointment",
    "Assessment",
    "AssessmentQuestion", 
    "AssessmentAnswer",
    "TherapyPlan",
    "TherapyPlanItem",
    "TherapySession",
    "Notification",
    "AuditLog"
]
