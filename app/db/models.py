from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient = Column(String(255), nullable=False)
    message = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
