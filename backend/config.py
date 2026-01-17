"""
Configuration settings for the Flask application
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rise-of-the-jaguar-secret-key-2024'
    
    # Database configuration
    # Use SQLite for development (no PostgreSQL needed)
    # For production, set DATABASE_URL environment variable
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "prompt_management.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration - use same key as SECRET_KEY for consistency
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # CORS configuration
    CORS_ORIGINS = ['http://localhost:5500', 'http://127.0.0.1:5500', 'http://localhost:3000']
    
    # AI Engine configuration
    AI_WEIGHTS = {
        'clarity': 0.4,
        'relevance': 0.4,
        'length': 0.2
    }
    
    # Prompt length thresholds
    MIN_PROMPT_LENGTH = 10
    MAX_PROMPT_LENGTH = 500
    OPTIMAL_MIN_LENGTH = 20
    OPTIMAL_MAX_LENGTH = 200


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
