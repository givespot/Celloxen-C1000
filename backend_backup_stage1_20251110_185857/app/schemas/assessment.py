from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from ..models.assessment import AssessmentType, AssessmentStatus, TherapyDomain, QuestionType

# Assessment Question schemas
class AssessmentQuestionBase(BaseModel):
    question_code: str = Field(..., max_length=50)
    question_text: str
    domain: TherapyDomain
    sub_category: Optional[str] = Field(None, max_length=100)
    question_type: QuestionType
    options: Optional[Dict[str, Any]] = None
    weight: Decimal = Field(default=Decimal("1.00"))
    reverse_scored: bool = False
    display_order: Optional[int] = None

class AssessmentQuestionCreate(AssessmentQuestionBase):
    follow_up_question_id: Optional[int] = None
    follow_up_trigger_condition: Optional[Dict[str, Any]] = None

class AssessmentQuestionResponse(AssessmentQuestionBase):
    id: int
    follow_up_question_id: Optional[int] = None
    follow_up_trigger_condition: Optional[Dict[str, Any]] = None
    active: bool
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Assessment Answer schemas
class AssessmentAnswerBase(BaseModel):
    question_id: int
    answer_value: str = Field(..., max_length=255)
    answer_text: Optional[str] = None

class AssessmentAnswerCreate(AssessmentAnswerBase):
    assessment_id: int

class AssessmentAnswerResponse(AssessmentAnswerBase):
    id: int
    assessment_id: int
    score_contribution: Optional[Decimal] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Base Assessment schema
class AssessmentBase(BaseModel):
    assessment_type: AssessmentType = AssessmentType.INITIAL

# Schema for creating an assessment
class AssessmentCreate(AssessmentBase):
    clinic_id: int
    patient_id: int

# Schema for updating an assessment
class AssessmentUpdate(BaseModel):
    assessment_type: Optional[AssessmentType] = None
    status: Optional[AssessmentStatus] = None
    questionnaire_started_at: Optional[datetime] = None
    questionnaire_completed_at: Optional[datetime] = None
    questions_answered: Optional[int] = None
    iridology_included: Optional[bool] = None
    iridology_left_image: Optional[str] = None
    iridology_right_image: Optional[str] = None
    iridology_analysis_result: Optional[str] = None
    diabetics_score: Optional[Decimal] = None
    chronic_pain_score: Optional[Decimal] = None
    anxiety_stress_score: Optional[Decimal] = None
    energy_vitality_score: Optional[Decimal] = None
    overall_wellness_score: Optional[Decimal] = None
    report_generated: Optional[bool] = None
    report_pdf_path: Optional[str] = None
    report_generated_at: Optional[datetime] = None

# Schema for assessment response
class AssessmentResponse(AssessmentBase):
    id: int
    assessment_number: str
    clinic_id: int
    patient_id: int
    status: AssessmentStatus
    questionnaire_started_at: Optional[datetime] = None
    questionnaire_completed_at: Optional[datetime] = None
    total_questions: int
    questions_answered: int
    iridology_included: bool
    iridology_left_image: Optional[str] = None
    iridology_right_image: Optional[str] = None
    iridology_analysis_result: Optional[str] = None
    diabetics_score: Optional[Decimal] = None
    chronic_pain_score: Optional[Decimal] = None
    anxiety_stress_score: Optional[Decimal] = None
    energy_vitality_score: Optional[Decimal] = None
    overall_wellness_score: Optional[Decimal] = None
    report_generated: bool
    report_pdf_path: Optional[str] = None
    report_generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    # Computed properties
    is_completed: bool
    completion_percentage: float
    
    # Relationships
    answers: List[AssessmentAnswerResponse] = []
    
    class Config:
        from_attributes = True

# Schema for assessment summary
class AssessmentSummary(BaseModel):
    id: int
    assessment_number: str
    assessment_type: AssessmentType
    status: AssessmentStatus
    overall_wellness_score: Optional[Decimal] = None
    completion_percentage: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schema for assessment scores
class AssessmentScores(BaseModel):
    diabetics_score: Optional[Decimal] = None
    chronic_pain_score: Optional[Decimal] = None
    anxiety_stress_score: Optional[Decimal] = None
    energy_vitality_score: Optional[Decimal] = None
    overall_wellness_score: Optional[Decimal] = None
    
    class Config:
        from_attributes = True
