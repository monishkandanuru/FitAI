"""Environment configuration; production requires persistent storage."""
import os
import secrets
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def database_url():
    value = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/fitai.db')
    if value.startswith(('postgres://', 'postgresql://')):
        value = 'postgresql+psycopg://' + value.split('://', 1)[1]
    return value

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(32)
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
    MAX_CONTENT_LENGTH = 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    AUTO_CREATE_DB = True

class DevelopmentConfig(Config):
    ENV = 'development'

class ProductionConfig(Config):
    ENV = 'production'
    SESSION_COOKIE_SECURE = True
    AUTO_CREATE_DB = False

class TestingConfig(Config):
    TESTING = True
    ENV = 'testing'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config_by_name = {'development': DevelopmentConfig, 'production': ProductionConfig,
                  'testing': TestingConfig, 'default': DevelopmentConfig}
