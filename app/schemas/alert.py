from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertBase(BaseModel):
    title: str
    description: Optional[str] = None
    link: str
    category: str
    published_at: datetime

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True