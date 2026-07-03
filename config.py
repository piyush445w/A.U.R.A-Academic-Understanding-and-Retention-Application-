"""
Flask Configuration Module
Intelligent Student Risk Monitoring & Decision Support System
"""

import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Determine project root - always use this file's location as base
# This ensures paths are correct regardless of where Python is invoked from
_PROJECT_ROOT = Path(__file__).resolve().parent

# Load environment variables from .env file in project root
load_dotenv(dotenv_path=_PROJECT_ROOT / '.env')


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    DEBUG = False
    TESTING = False
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Session settings - persist for 7 days
    PERMANENT_SESSION_LIFETIME = 7 * 24 * 60 * 60  # 7 days in seconds
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database settings - Always use _PROJECT_ROOT to ensure consistent path
    BASE_DIR = str(_PROJECT_ROOT)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{_PROJECT_ROOT / "instance" / "student_risk.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application settings
    APP_NAME = 'A.U.R.A - Academic Understanding and Retention Application'
    APP_VERSION = '1.0.0'
    
    # ML Model settings - Use _PROJECT_ROOT for consistent paths
    MODEL_PATH = str(_PROJECT_ROOT / 'models' / 'trained')
    DATASET_PATH = str(_PROJECT_ROOT / 'datasets')
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = str(_PROJECT_ROOT / 'app' / 'static' / 'uploads')
    
    # Email settings (for notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    
    # Risk thresholds
    HIGH_RISK_THRESHOLD = 0.7
    MEDIUM_RISK_THRESHOLD = 0.4
    LOW_RISK_THRESHOLD = 0.2


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    # Use secure random key even in development
    WTF_CSRF_TIME_LIMIT = 7200  # 2 hours for dev


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Force HTTPS for session cookies in production


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Validate required env vars - SECRET_KEY has fallback to secrets.token_hex(32) so it's always set
# No validation needed as we have secure fallbacks
