from fastapi import FastAPI
from app.config import get_settings
from app.db.base import Base, engine
from app.api.routes import router
import logging
from logging.handlers import RotatingFileHandler
import os
from fastapi.middleware.cors import CORSMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=get_settings().PROJECT_NAME,
    openapi_url=f"{get_settings().API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix=get_settings().API_V1_STR)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            'logs/app.log',
            maxBytes=1024 * 1024,
            backupCount=5
        )
    ]
)

# Set specific log levels for different loggers
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)  # Reduce SQLAlchemy logging
logging.getLogger('app').setLevel(logging.INFO)  # Ensure app logs are captured
logging.getLogger('uvicorn').setLevel(logging.INFO)  # For uvicorn logs
logging.getLogger('fastapi').setLevel(logging.INFO)  # For FastAPI logs