"""
Configuration module for GEX Analyzer
"""

import os
from datetime import datetime

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', True)
    TESTING = False
    
    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

# Select configuration class based on environment
def get_config():
    """Get appropriate config class based on environment"""
    config_name = os.environ.get('FLASK_ENV', 'development').lower()
    if config_name == 'production':
        return ProductionConfig
    elif config_name == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig

Config = get_config()
