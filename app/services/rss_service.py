import feedparser
from datetime import datetime
from typing import Optional
from app.schemas.entry import EntryCreate
from app.schemas.feed import FeedUpdate
from app.services.entry_service import EntryService
from app.services.feed_service import FeedService
from fastapi import HTTPException
import pytz
from dateutil import parser
import logging
from urllib.parse import urlparse, parse_qsl

logger = logging.getLogger(__name__)

class RSSService:
    def __init__(self, db_session):
        self.entry_service = EntryService(db_session)
        self.feed_service = FeedService(db_session)
        self.db = db_session

    def extract_publisher(self, url: str) -> Optional[str]:
        try:
            # Parse the main URL and extract the query parameter 'url'
            parsed_url = urlparse(url)
            query_dict = dict(parse_qsl(parsed_url.query))
            
            # Get the target URL from the 'url' parameter
            if 'url' in query_dict:
                nested_url = query_dict['url']
                nested_parsed = urlparse(nested_url)
                # Extract the domain (netloc)
                domain = nested_parsed.netloc
                # Remove subdomains like 'www' and return the base domain
                parts = domain.split('.')
                if len(parts) >= 2:
                    return ".".join(parts[-2:])
            return None
        except Exception as e:
            logger.warning(f"Failed to extract publisher from URL {url}: {str(e)}")
            return None

    def parse_date(self, date_str: str) -> datetime:
        """Convert various date formats to UTC datetime"""
        try:
            dt = parser.parse(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pytz.UTC)
            return dt
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}', using current time. Error: {str(e)}")
            return datetime.now(pytz.UTC)

    def fetch_and_parse_feed(self, feed_id: str) -> int:
        """
        Fetch and parse a specific feed
        Returns number of new entries created
        """
        logger.info(f"Starting fetch and parse for feed ID: {feed_id}")
        try:
            # Get feed from database
            feed = self.feed_service.get_feed(feed_id)
            logger.info(f"Processing feed: {feed.name or feed.url}")
            
            # Parse RSS feed
            logger.debug(f"Fetching RSS feed from URL: {feed.url}")
            parsed_feed = feedparser.parse(str(feed.url))
            
            if parsed_feed.bozo and parsed_feed.bozo_exception:
                error_msg = f"Feed parsing error for {feed.url}: {str(parsed_feed.bozo_exception)}"
                logger.error(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)

            # Log feed metadata
            logger.debug(f"Feed metadata: {parsed_feed.feed.get('title', 'No title')} - "
                        f"Version: {parsed_feed.version}")

            # Prepare entries
            new_entries = []
            logger.info(f"Found {len(parsed_feed.entries)} entries in feed")
            
            for index, item in enumerate(parsed_feed.entries):
                try:
                    # Log raw entry data for debugging
                    logger.debug(f"Raw entry data: {item}")
                    
                    # Extract all available attributes
                    entry_id = item.get('id', '')
                    title = item.get('title', 'No title'). replace('\n', '')
                    link = item.get('link', '')
                    published = item.get('published')
                    updated = item.get('updated')
                    content = item.get('content', [{'value': ''}])[0].get('value') if item.get('content') else ''

                    # Parse dates
                    published_at = self.parse_date(published) if published else datetime.now(pytz.UTC)
                    updated_at = self.parse_date(updated) if updated else published_at
                    
                    # Parse publisher
                    publisher = self.extract_publisher(link)
                    
                    # Create entry object
                    entry = EntryCreate(
                        title=title,
                        content=content,
                        link=link,
                        published_at=published_at,
                        updated_at=updated_at,
                        feed_id=feed.id,
                        entry_id=entry_id,
                        publisher=publisher,
                        is_read=False,
                        is_bookmarked=False
                    )
                    
                    # Log successful entry creation
                    logger.info(f"Successfully created entry: {entry.title[:50]}... at {entry.published_at}")
                    new_entries.append(entry)
                    
                    # Log detailed entry info at debug level
                    logger.debug(f"""Processed entry {index + 1}:
                        Title: {entry.title}
                        Link: {entry.link}
                        Published: {entry.published_at}
                        Content length: {len(entry.content)} chars
                    """)
                    
                except Exception as e:
                    logger.error(f"Error processing entry {index + 1}: {str(e)}")
                    logger.exception("Full error details:")  # This logs the full stack trace
                    continue  # Skip this entry but continue processing others

            # Batch create entries
            logger.info(f"Attempting to save {len(new_entries)} new entries")
            created_entries = self.entry_service.create_entries_batch(new_entries)

            # Update feed's last_fetched timestamp
            self.feed_service.update_feed(
                feed_id,
                FeedUpdate(
                    last_fetched=datetime.now(pytz.UTC)
                )
            )

            logger.info(f"Successfully processed feed {feed_id}: {len(created_entries)} new entries created")
            
            # Log detailed results
            logger.debug("Parse results: " + 
                f"\nFeed: {feed.name or feed.url}" +
                f"\nTotal entries found: {len(parsed_feed.entries)}" +
                f"\nNew entries created: {len(created_entries)}" +
                f"\nLast entry title: {new_entries[-1].title if new_entries else 'None'}"
            )
            
            return len(created_entries)

        except HTTPException:
            raise  # Re-raise HTTP exceptions as they're already properly formatted
        except Exception as e:
            error_msg = f"Error processing feed {feed_id}: {str(e)}"
            logger.exception(error_msg)  # This logs the full stack trace
            raise HTTPException(status_code=500, detail=error_msg)

    def fetch_all_feeds(self) -> dict:
        """
        Fetch and parse all feeds
        Returns dictionary with results for each feed
        """
        logger.info("Starting fetch_all_feeds operation")
        results = {}
        feeds = self.feed_service.get_feeds()
        
        logger.info(f"Processing {len(feeds)} feeds")
        
        for feed in feeds:
            try:
                logger.info(f"Processing feed: {feed.name or feed.url}")
                new_entries = self.fetch_and_parse_feed(feed.id)
                results[feed.id] = {
                    "status": "success",
                    "new_entries": new_entries
                }
                logger.info(f"Successfully processed feed {feed.id}: {new_entries} new entries")
            except Exception as e:
                error_msg = f"Error processing feed {feed.id}: {str(e)}"
                logger.error(error_msg)
                results[feed.id] = {
                    "status": "error",
                    "error": str(e)
                }

        logger.info("Completed fetch_all_feeds operation")
        logger.debug(f"Final results: {results}")
        return results

    def validate_feed_url(self, url: str) -> bool:
        """
        Validate if URL is a valid RSS feed
        Returns True if valid, False otherwise
        """
        logger.debug(f"Validating RSS feed URL: {url}")
        try:
            parsed = feedparser.parse(url)
            if parsed.bozo:
                logger.warning(f"Invalid feed URL {url}: {parsed.bozo_exception}")
                return False
                
            # Check if feed has required elements
            is_valid = bool(parsed.feed and parsed.entries)
            if is_valid:
                logger.debug(f"Successfully validated feed URL: {url}")
            else:
                logger.warning(f"Invalid feed URL {url}: Missing required elements")
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating feed URL {url}: {str(e)}")
            return False