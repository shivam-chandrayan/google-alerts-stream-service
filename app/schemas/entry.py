from pydantic import BaseModel
from datetime import datetime

class EntryBase(BaseModel):
    title: str
    content: str
    link: str
    published_at: datetime
    updated_at: datetime

class EntryCreate(EntryBase):
    feed_id: str

class Entry(EntryBase):
    id: str
    feed_id: str
    created_at: datetime

    class Config:
        from_attributes = True