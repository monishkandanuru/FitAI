"""
FitAI Configuration Module
Defines settings for Development, Production, and Testing environments.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base Configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fitai-secret-key-change-in-production-2026')
    DEBUG = False
    TESTING = False
    
    # SQLite Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'fitai.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Storage Locations
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    REPORT_FOLDER = os.path.join(BASE_DIR, 'reports')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload limit


class DevelopmentConfig(Config):
    """Development Environment Configuration"""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Production Environment Configuration"""
    DEBUG = False
    ENV = 'production'


class TestingConfig(Config):
    """Testing Environment Configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    ENV = 'testing'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
