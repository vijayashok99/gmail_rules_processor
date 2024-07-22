from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    message_id = Column(String(255), unique=True, nullable=False)
    sender = Column(String(255), nullable=False)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(255))
    body = Column(Text)
    received_date = Column(DateTime(timezone=True), nullable=False)

    @classmethod
    def create(cls, message_id, sender, recipient, subject, body, received_date):
        return cls(
            message_id=message_id,
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            received_date=cls.ensure_offset_aware(received_date)
        )

    @staticmethod
    def ensure_offset_aware(dt):
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
