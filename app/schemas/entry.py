from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class EntryBase(BaseModel):
    title: str
    content: str
    link: str
    publisher: Optional[str] = None
    published_at: datetime
    updated_at: datetime
    is_read: bool = False
    is_bookmarked: bool = False

class EntryStatus(BaseModel):
    read: bool = False
    bookmarked: bool = False

class EntryCreate(EntryBase):
    feed_id: str

class Entry(EntryBase):
    id: str
    feed_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedEntriesResponse(BaseModel):
    entries: List[Entry]
    total_count: int

    class Config:
        from_attributes = True

