from sqlalchemy import Column, BigInteger, String, Enum, ForeignKey, DateTime, Integer, Boolean, Text, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class AssessmentType(str, enum.Enum):
    INITIAL = "initial"
    MID_COURSE = "mid_course"
    FINAL = "final"
    FOLLOW_UP = "follow_up"

class AssessmentStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class TherapyDomain(str, enum.Enum):
    DIABETICS = "diabetics"
    CHRONIC_PAIN = "chronic_pain"
    ANXIETY_STRESS = "anxiety_stress"
    ENERGY_VITALITY = "energy_vitality"

class QuestionType(str, enum.Enum):
    SCALE_1_5 = "scale_1_5"
    YES_NO = "yes_no"
    MULTIPLE_CHOICE = "multiple_choice"
    SEVERITY_1_10 = "severity_1_10"

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(BigInteger, primary_key=True, index=True)
    assessment_number = Column(String(50), unique=True, nullable=False)
    clinic_id = Column(BigInteger, ForeignKey("clinics.id"), nullable=False)
    patient_id = Column(BigInteger, ForeignKey("patients.id"), nullable=False)
    assessment_type = Column(Enum(AssessmentType), default=AssessmentType.INITIAL)
    status = Column(Enum(AssessmentStatus), default=AssessmentStatus.IN_PROGRESS)
    questionnaire_started_at = Column(DateTime(timezone=True), nullable=True)
    questionnaire_completed_at = Column(DateTime(timezone=True), nullable=True)
    total_questions = Column(Integer, default=35)
    questions_answered = Column(Integer, default=0)
    iridology_included = Column(Boolean, default=False)
    iridology_left_image = Column(String(255), nullable=True)
    iridology_right_image = Column(String(255), nullable=True)
    iridology_analysis_result = Column(Text, nullable=True)
    diabetics_score = Column(DECIMAL(5,2), nullable=True)
    chronic_pain_score = Column(DECIMAL(5,2), nullable=True)
    anxiety_stress_score = Column(DECIMAL(5,2), nullable=True)
    energy_vitality_score = Column(DECIMAL(5,2), nullable=True)
    overall_wellness_score = Column(DECIMAL(5,2), nullable=True)
    report_generated = Column(Boolean, default=False)
    report_pdf_path = Column(String(255), nullable=True)
    report_generated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    
    @property
    def is_completed(self) -> bool:
        return self.status == AssessmentStatus.COMPLETED
    
    @property
    def completion_percentage(self) -> float:
        if self.total_questions == 0:
            return 0.0
        return (self.questions_answered / self.total_questions) * 100

class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"
    
    id = Column(BigInteger, primary_key=True, index=True)
    question_code = Column(String(50), unique=True, nullable=False)
    question_text = Column(Text, nullable=False)
    domain = Column(Enum(TherapyDomain), nullable=False)
    sub_category = Column(String(100), nullable=True)
    question_type = Column(Enum(QuestionType), nullable=False)
    options = Column(JSON, nullable=True)
    weight = Column(DECIMAL(3,2), default=1.00)
    reverse_scored = Column(Boolean, default=False)
    follow_up_question_id = Column(BigInteger, ForeignKey("assessment_questions.id"), nullable=True)
    follow_up_trigger_condition = Column(JSON, nullable=True)
    active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    display_order = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class AssessmentAnswer(Base):
    __tablename__ = "assessment_answers"
    
    id = Column(BigInteger, primary_key=True, index=True)
    assessment_id = Column(BigInteger, ForeignKey("assessments.id"), nullable=False)
    question_id = Column(BigInteger, ForeignKey("assessment_questions.id"), nullable=False)
    answer_value = Column(String(255), nullable=False)
    answer_text = Column(Text, nullable=True)
    score_contribution = Column(DECIMAL(5,2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
