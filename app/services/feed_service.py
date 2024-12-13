from sqlalchemy.orm import Session
from app.models.feed import Feed
from app.schemas.feed import FeedCreate, FeedUpdate
from fastapi import HTTPException
from typing import List
import logging

class FeedService:
    def __init__(self, db: Session):
        self.db = db

    def create_feed(self, feed: FeedCreate) -> Feed:
        try:
            feed_data = feed.model_dump()
            feed_data['url'] = str(feed_data['url'])

            existing_feed = self.db.query(Feed).filter(Feed.url == feed_data['url']).first()
            if existing_feed:
                raise HTTPException(
                    status_code=400,
                    detail="Feed with this URL already exists"
                )

            db_feed = Feed(**feed_data)
            self.db.add(db_feed)
            self.db.commit()
            self.db.refresh(db_feed)
            return db_feed
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error creating feed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_feeds(self) -> List[Feed]:
        try:
            feeds = self.db.query(Feed).order_by(Feed.created_at.desc()).all()
            logging.debug(f"Retrieved {len(feeds)} feeds from database")
            return feeds
        except Exception as e:
            logging.exception(f"Database error in get_feeds: {type(e).__name__}, Message: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )

    def get_feed(self, feed_id: str) -> Feed:
        feed = self.db.query(Feed).filter(Feed.id == feed_id).first()
        if not feed:
            raise HTTPException(status_code=404, detail="Feed not found")
        return feed

    def update_feed(self, feed_id: str, feed_update: FeedUpdate) -> Feed:
        feed = self.get_feed(feed_id)
        for field, value in feed_update.model_dump(exclude_unset=True).items():
            setattr(feed, field, value)
        self.db.commit()
        self.db.refresh(feed)
        return feed

    def delete_feed(self, feed_id: str) -> bool:
        feed = self.get_feed(feed_id)
        self.db.delete(feed)
        self.db.commit()
        return True

    # def get_feed_stats(self, feed_id: str) -> FeedStats:
    #     feed = self.get_feed(feed_id)
    #     total_entries = len(feed.entries)
    #     return FeedStats(
    #         total_entries=total_entries,
    #         last_fetched=feed.last_fetched
    #     )