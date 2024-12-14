from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.base import get_db
from app.schemas.feed import FeedCreate, Feed, FeedUpdate
from app.schemas.entry import Entry, PaginatedEntriesResponse, EntryStatus
from app.services.health_service import HealthService
from app.services.feed_service import FeedService
from app.services.entry_service import EntryService
from app.services.rss_service import RSSService
import logging

logger = logging.getLogger('app.api.routes')

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Check the health of all services"""
    logger.info("Health check endpoint called")
    try:
        health_service = HealthService(db)
        return health_service.check_all()
    except HTTPException as e:
        logger.error(f"Health check failed with HTTP error: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Health check failed with unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

# Feed routes
@router.post("/feeds/", response_model=Feed)
def create_feed(
    feed: FeedCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new feed and fetch its entries in the background"""
    logger.info(f"Attempting to create feed with URL: {feed.url}")
    
    try:
        feed_service = FeedService(db)
        rss_service = RSSService(db)
        
        # Validate feed URL
        logger.debug(f"Validating RSS feed URL: {feed.url}")
        if not rss_service.validate_feed_url(str(feed.url)):
            logger.warning(f"Invalid RSS feed URL: {feed.url}")
            raise HTTPException(
                status_code=400,
                detail="Invalid RSS feed URL. Please provide a valid RSS/Atom feed URL"
            )
        
        # Create feed
        logger.debug("Creating feed in database")
        try:
            db_feed = feed_service.create_feed(feed)
        except HTTPException as e:
            if e.status_code == 400:
                logger.warning(f"Feed creation failed: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during feed creation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while creating feed"
            )
        
        # Schedule initial fetch
        logger.info(f"Scheduling initial fetch for feed ID: {db_feed.id}")
        try:
            background_tasks.add_task(rss_service.fetch_and_parse_feed, db_feed.id)
        except Exception as e:
            logger.error(f"Failed to schedule background task: {str(e)}")
            # Don't raise here as feed was created successfully
            # Just log the error and return the feed
        
        logger.info(f"Successfully created feed with ID: {db_feed.id}")
        return db_feed
        
    except HTTPException:
        # Re-raise HTTP exceptions as they're already properly formatted
        raise
    except Exception as e:
        logger.exception("Unexpected error in create_feed endpoint")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while processing request: {str(e)}"
        )

@router.get("/feeds/", response_model=List[Feed])
def get_feeds(db: Session = Depends(get_db)):
    """Get all feeds"""
    logger.info("Fetching all feeds")
    try:
        feed_service = FeedService(db)
        feeds = feed_service.get_feeds()
        if not feeds:
            logger.info("No feeds found in database")
            return []
            
        logger.info(f"Successfully fetched {len(feeds)} feeds")
        return feeds
    except Exception as e:
        logger.exception(f"Error in get_feeds: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while fetching feeds: {str(e)}"
        )

@router.get("/feeds/{feed_id}", response_model=Feed)
def get_feed(feed_id: str, db: Session = Depends(get_db)):
    """Get a specific feed"""
    feed_service = FeedService(db)
    return feed_service.get_feed(feed_id)

@router.put("/feeds/{feed_id}", response_model=Feed)
def update_feed(
    feed_id: str,
    feed_update: FeedUpdate,
    db: Session = Depends(get_db)
):
    """Update a feed"""
    feed_service = FeedService(db)
    return feed_service.update_feed(feed_id, feed_update)

@router.delete("/feeds/{feed_id}")
def delete_feed(feed_id: str, db: Session = Depends(get_db)):
    """Delete a feed and its associated entries"""
    logger.info(f"Attempting to delete feed with ID: {feed_id}")
    
    try:
        feed_service = FeedService(db)
        
        # First check if the feed exists
        existing_feed = feed_service.get_feed(feed_id)
        if not existing_feed:
            logger.warning(f"Feed with ID {feed_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Feed with ID {feed_id} not found"
            )
            
        # Attempt to delete the feed
        result = feed_service.delete_feed(feed_id)
        
        logger.info(f"Successfully deleted feed with ID: {feed_id}")
        return {
            "status": "success",
            "message": f"Feed {feed_id} has been deleted",
            "deleted": True
        }
        
    except HTTPException as he:
        # Re-raise HTTP exceptions as they're already properly formatted
        raise he
        
    except Exception as e:
        logger.exception(f"Unexpected error while deleting feed {feed_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while deleting feed: {str(e)}"
        )

# Entry routes
@router.get("/entries/", response_model=PaginatedEntriesResponse)
def get_entries(
    limit: int = Query(10, description="Number of items to fetch"),
    skip: int = Query(0, description="Number of items to skip"),
    keywords: List[str] = Query(None, description="List of keywords to filter feeds"),
    db: Session = Depends(get_db)
):
    """Get all entries with optional keyword filtering"""
    logger.info(f"Fetching entries with skip={skip}, limit={limit}, keywords={keywords}")
    try:
        entry_service = EntryService(db)
        entries = entry_service.get_entries(skip=skip, limit=limit, keywords=keywords)
        logger.debug(f"Retrieved {len(entries)} entries")
        
        # Log first entry for debugging (if any exist)
        if entries and logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Sample entry: {entries[0].__dict__}")
            
        return entries
    except Exception as e:
        logger.exception(f"Error fetching entries: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while fetching entries: {str(e)}"
        )

@router.put("/entries/{entry_id}/status", response_model=Entry)
def update_entry_status(entry_id: str, status: EntryStatus, db: Session = Depends(get_db)):
    """Update the status of an entry"""
    entry_service = EntryService(db)
    return entry_service.update_entry_status(entry_id, status)

@router.get("/entries/bookmarked", response_model=PaginatedEntriesResponse)
def get_bookmarked_entries(
    limit: int = Query(10, description="Number of items to fetch"),
    skip: int = Query(0, description="Number of items to skip"),
    keywords: List[str] = Query(None, description="List of keywords to filter feeds"),
    db: Session = Depends(get_db)
):
    """Get all bookmarked entries with optional keyword filtering"""
    logger.info(f"Fetching bookmarked entries with skip={skip}, limit={limit}, keywords={keywords}")
    try:
        entry_service = EntryService(db)
        entries = entry_service.get_bookmarked_entries(skip=skip, limit=limit, keywords=keywords)
        logger.debug(f"Retrieved {len(entries)} entries")

        return entries
    except Exception as e:
        logger.exception(f"Error fetching entries: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while fetching entries: {str(e)}"
        )

@router.get("/feeds/{feed_id}/entries", response_model=List[Entry])
def get_feed_entries(
    feed_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get entries for a specific feed"""
    entry_service = EntryService(db)
    return entry_service.get_feed_entries(feed_id, skip, limit)

# RSS operations
@router.post("/feeds/{feed_id}/refresh")
def refresh_feed(
    feed_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger a feed refresh"""
    rss_service = RSSService(db)
    background_tasks.add_task(rss_service.fetch_and_parse_feed, feed_id)
    return {"message": "Feed refresh scheduled"}

@router.post("/feeds/refresh-all")
def refresh_all_feeds(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Refresh all feeds"""
    rss_service = RSSService(db)
    background_tasks.add_task(rss_service.fetch_all_feeds)
    return {"message": "All feeds refresh scheduled"}