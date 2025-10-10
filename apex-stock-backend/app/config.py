import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration with common settings"""
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///apex_stock.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Saves memory
    
    # JWT Settings
    JWT_TOKEN_LOCATION = ['headers']  # Tokens come in request headers
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'  # Format: "Bearer <token>"
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour in seconds
    JWT_VERIFY_SUB = False
    
    # CORS (allows React to talk to Flask)
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000,http://localhost:80,http://localhost').split(',')

class DevelopmentConfig(Config):
    """Development-specific settings"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production-specific settings"""
    DEBUG = False
    TESTING = False

# Choose config based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}