from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.entry import Entry
from app.schemas.entry import EntryCreate, EntryStatus
from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime
from app.models.feed import Feed
from sqlalchemy import or_
import logging

class EntryService:
    def __init__(self, db: Session):
        self.db = db

    def create_entry(self, entry: EntryCreate) -> Entry:
        """Create a new entry if it doesn't exist"""
        try:
            # Check if entry with same link already exists
            existing_entry = self.db.query(Entry).filter(Entry.link == entry.link).first()
            if existing_entry:
                return existing_entry

            db_entry = Entry(**entry.model_dump())
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            return db_entry
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_entries(
        self,
        skip: int = 0,
        limit: int = 10,
        keywords: Optional[List[str]] = None
    ) -> List[Entry]:
        """
        Get entries with optional keyword filtering
        Returns newest entries first
        """
        query = self.db.query(Entry)

        if keywords:
            query = query.join(Feed)
            keyword_filters = [Feed.keyword.ilike(f"%{keyword}%") for keyword in keywords]
            query = query.filter(or_(*keyword_filters))

        total_count = query.count()
        query = query.order_by(desc(Entry.published_at))
        entries = query.offset(skip).limit(limit).all()

        return {
            "entries": entries,
            "total_count": total_count
        }

    def get_entry(self, entry_id: str) -> Entry:
        """Get a specific entry by ID"""
        entry = self.db.query(Entry).filter(Entry.id == entry_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        return entry

    def get_bookmarked_entries(
        self,
        skip: int = 0,
        limit: int = 10,
        keywords: Optional[List[str]] = None
    ) -> List[Entry]:
        """
        Get bookmarked entries with optional keyword filtering
        Returns newest entries first
        """
        query = self.db.query(Entry)

        # Filter for bookmarked entries
        query = query.filter(Entry.is_bookmarked == True)

        if keywords:
            query = query.join(Feed)
            keyword_filters = [Feed.keyword.ilike(f"%{keyword}%") for keyword in keywords]
            query = query.filter(or_(*keyword_filters))

        total_count = query.count()
        query = query.order_by(desc(Entry.published_at))
        entries = query.offset(skip).limit(limit).all()

        logging.info(f"bookmarked entries: {entries}")

        return {
            "entries": entries,
            "total_count": total_count
        }


    def create_entries_batch(self, entries: List[EntryCreate]) -> List[Entry]:
        """Create multiple entries at once, skipping existing ones"""
        try:
            created_entries = []
            for entry_data in entries:
                # Check if entry already exists
                existing_entry = self.db.query(Entry).filter(
                    Entry.link == entry_data.link
                ).first()
                
                if existing_entry:
                    created_entries.append(existing_entry)
                    continue

                db_entry = Entry(**entry_data.model_dump())
                self.db.add(db_entry)
                created_entries.append(db_entry)

            self.db.commit()
            return created_entries
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_feed_entries(
        self,
        feed_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Entry]:
        """Get entries for a specific feed"""
        return self.db.query(Entry)\
            .filter(Entry.feed_id == feed_id)\
            .order_by(desc(Entry.published_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

    def count_entries(self, feed_id: Optional[str] = None) -> int:
        """Count total entries, optionally for a specific feed"""
        query = self.db.query(Entry)
        if feed_id:
            query = query.filter(Entry.feed_id == feed_id)
        return query.count()
    
    def update_entry_status(self, entry_id: str, status: EntryStatus) -> Entry:
        """Update the status of an entry"""
        entry = self.get_entry(entry_id)
        logging.info(f"Updating entry status: {entry_id} - {status}")
        entry.is_read = status.read
        entry.is_bookmarked = status.bookmarked
        self.db.commit()
        return entry