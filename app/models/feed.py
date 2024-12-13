from sqlalchemy import Column, String, DateTime, TypeDecorator
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base
from pydantic import HttpUrl, ValidationError

class URLType(TypeDecorator):
    """Custom SQLAlchemy type for URLs with validation"""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert to string before storing in DB"""
        if value is not None:
            if isinstance(value, HttpUrl):
                return str(value)
            return value
        return None

    def process_result_value(self, value, dialect):
        """Keep as string when reading from DB"""
        return value

class Feed(Base):
    __tablename__ = "feeds"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(URLType, nullable=False, unique=True)
    keyword = Column(String(100), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    last_fetched = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with entries
    entries = relationship("Entry", back_populates="feed", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Feed {self.keyword}>"