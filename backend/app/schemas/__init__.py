# Import all schemas here for easy access
from .user import UserCreate, UserUpdate, UserResponse, UserLogin, Token
from .clinic import ClinicCreate, ClinicUpdate, ClinicResponse
from .patient import PatientCreate, PatientUpdate, PatientResponse
from .appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from .assessment import AssessmentCreate, AssessmentUpdate, AssessmentResponse
from .therapy_plan import TherapyPlanCreate, TherapyPlanUpdate, TherapyPlanResponse
from .therapy_session import TherapySessionCreate, TherapySessionUpdate, TherapySessionResponse
from .notification import NotificationCreate, NotificationResponse

# Export all schemas
__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin", "Token",
    "ClinicCreate", "ClinicUpdate", "ClinicResponse",
    "PatientCreate", "PatientUpdate", "PatientResponse", 
    "AppointmentCreate", "AppointmentUpdate", "AppointmentResponse",
    "AssessmentCreate", "AssessmentUpdate", "AssessmentResponse",
    "TherapyPlanCreate", "TherapyPlanUpdate", "TherapyPlanResponse",
    "TherapySessionCreate", "TherapySessionUpdate", "TherapySessionResponse",
    "NotificationCreate", "NotificationResponse"
]
