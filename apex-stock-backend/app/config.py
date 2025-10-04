import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT-SECRET-KEY', 'jwt-secret-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///apex_stock.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Settings
    JWT_TOKEN_LOCATION = ['headers']  # Tokens come in request headers
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'  # Format: "Bearer <token>"
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour in seconds
    
    # CORS (allows React to talk to Flask)
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000']


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    

config = {
    'development' : DevelopmentConfig,
    'production' : ProductionConfig,
    'default' : DevelopmentConfig
}
