from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class FeedBase(BaseModel):
    url: HttpUrl
    keyword: str
    name: Optional[str] = None

class FeedCreate(FeedBase):
    pass

class FeedUpdate(BaseModel):
    keyword: Optional[str] = None
    name: Optional[str] = None

class Feed(FeedBase):
    id: str
    last_fetched: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True