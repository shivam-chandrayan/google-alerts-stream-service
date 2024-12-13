from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.rss_service import RSSService
from fastapi import HTTPException

class HealthService:
    def __init__(self, db: Session):
        self.db = db
        self.rss_service = RSSService(db)

    def check_database(self) -> bool:
        """Check if database is accessible"""
        try:
            # Try to execute a simple query
            self.db.execute(text('SELECT 1'))
            return True
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Database health check failed: {str(e)}")

    def check_rss_service(self) -> bool:
        """Check if RSS service is working"""
        try:
            # Try to validate a known good RSS URL
            test_url = "https://news.google.com/rss"
            return self.rss_service.validate_feed_url(test_url)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"RSS service health check failed: {str(e)}")

    def check_all(self) -> dict:
        """Run all health checks"""
        return {
            "status": "healthy",
            "database": self.check_database(),
            "rss_service": self.check_rss_service(),
            "version": "1.0.0"
        }