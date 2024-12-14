from sqlalchemy.orm import Session
from app.models.alert import Alert
from typing import List
from app.schemas.alert import AlertCreate
from fastapi import HTTPException

class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def get_alerts(self, skip: int = 0, limit: int = 100) -> List[Alert]:
        try:
            return self.db.query(Alert).order_by(Alert.published_at.desc()).offset(skip).limit(limit).all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def create_alert(self, alert: AlertCreate) -> Alert:
        try:
            db_alert = Alert(**alert.model_dump())
            self.db.add(db_alert)
            self.db.commit()
            self.db.refresh(db_alert)
            return db_alert
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))