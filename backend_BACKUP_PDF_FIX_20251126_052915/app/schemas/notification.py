from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from ..models.notification import RecipientType, NotificationChannel, NotificationStatus

# Base Notification schema
class NotificationBase(BaseModel):
    recipient_type: RecipientType
    recipient_id: int
    notification_type: str = Field(..., max_length=100)
    channel: NotificationChannel
    subject: Optional[str] = Field(None, max_length=255)
    message: str
    related_entity_type: Optional[str] = Field(None, max_length=50)
    related_entity_id: Optional[int] = None

# Schema for creating a notification
class NotificationCreate(NotificationBase):
    pass

# Schema for updating a notification
class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None
    read: Optional[bool] = None
    read_at: Optional[datetime] = None

# Schema for notification response
class NotificationResponse(NotificationBase):
    id: int
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int
    read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    
    # Computed properties
    is_sent: bool
    is_failed: bool
    can_retry: bool
    is_read: bool
    
    class Config:
        from_attributes = True

# Schema for notification summary
class NotificationSummary(BaseModel):
    id: int
    notification_type: str
    channel: NotificationChannel
    subject: Optional[str] = None
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schema for email notification
class EmailNotification(BaseModel):
    to_email: str
    subject: str
    message: str
    html_content: Optional[str] = None
    attachments: Optional[Dict[str, str]] = None  # filename: file_path

# Schema for SMS notification
class SMSNotification(BaseModel):
    to_phone: str
    message: str = Field(..., max_length=1600)  # SMS character limit

# Schema for in-app notification
class InAppNotification(BaseModel):
    user_id: int
    title: str
    message: str
    action_url: Optional[str] = None
    icon: Optional[str] = None

# Schema for notification preferences
class NotificationPreferences(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = True
    in_app_enabled: bool = True
    push_enabled: bool = True
    appointment_reminders: bool = True
    session_reminders: bool = True
    assessment_notifications: bool = True
    therapy_plan_notifications: bool = True
    marketing_notifications: bool = False
    
    class Config:
        from_attributes = True

# Schema for bulk notification
class BulkNotificationCreate(BaseModel):
    recipient_ids: list[int]
    recipient_type: RecipientType
    notification_type: str
    channel: NotificationChannel
    subject: Optional[str] = None
    message: str
    related_entity_type: Optional[str] = None
    
# Schema for notification template
class NotificationTemplate(BaseModel):
    template_name: str
    channel: NotificationChannel
    subject_template: Optional[str] = None
    message_template: str
    variables: Dict[str, str]  # Available variables for template
    
    class Config:
        from_attributes = True
