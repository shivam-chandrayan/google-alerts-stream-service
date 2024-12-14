from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base

class Entry(Base):
    __tablename__ = "entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    link = Column(String, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    feed_id = Column(String(36), ForeignKey("feeds.id"), nullable=False)
    publisher = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)
    is_bookmarked = Column(Boolean, default=False)

    # Relationship with feed
    feed = relationship("Feed", back_populates="entries")

    def __repr__(self):
        return f"<Entry {self.title}>"