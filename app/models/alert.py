from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class Alert(Base):
    """
    Alert model for storing Google Alerts data
    """
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    link = Column(String, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<Alert {self.title}>"