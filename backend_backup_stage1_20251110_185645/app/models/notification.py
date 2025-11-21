from sqlalchemy import Column, BigInteger, String, Enum, DateTime, Boolean, Text, Integer
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class RecipientType(str, enum.Enum):
    PATIENT = "patient"
    CLINIC_STAFF = "clinic_staff"
    SUPER_ADMIN = "super_admin"

class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    PUSH = "push"

class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(BigInteger, primary_key=True, index=True)
    recipient_type = Column(Enum(RecipientType), nullable=False)
    recipient_id = Column(BigInteger, nullable=False)
    notification_type = Column(String(100), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(BigInteger, nullable=True)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    @property
    def is_sent(self) -> bool:
        return self.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED]
    
    @property
    def is_failed(self) -> bool:
        return self.status in [NotificationStatus.FAILED, NotificationStatus.BOUNCED]
    
    @property
    def can_retry(self) -> bool:
        return self.is_failed and self.retry_count < 3
    
    @property
    def is_read(self) -> bool:
        return self.read and self.read_at is not None
