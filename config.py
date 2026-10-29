"""
FitAI Configuration Module
Defines settings for Development, Production, Vercel Serverless, and Testing environments.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'))


def _resolve_database_uri() -> str:
    """Resolve database URI supporting PostgreSQL (Vercel/Neon/Supabase) and SQLite fallback."""
    raw_url = (
        os.environ.get('DATABASE_URL')
        or os.environ.get('POSTGRES_URL')
        or os.environ.get('SQLALCHEMY_DATABASE_URI')
    )
    if raw_url:
        if raw_url.startswith('postgres://'):
            raw_url = raw_url.replace('postgres://', 'postgresql+psycopg://', 1)
        elif raw_url.startswith('postgresql://') and '+psycopg' not in raw_url:
            try:
                import psycopg  # noqa: F401
                raw_url = raw_url.replace('postgresql://', 'postgresql+psycopg://', 1)
            except ImportError:
                pass
        return raw_url

    if IS_VERCEL:
        # Vercel serverless filesystem is read-only except /tmp
        return 'sqlite:////tmp/fitai.db'

    return f"sqlite:///{os.path.join(BASE_DIR, 'fitai.db')}"


class Config:
    """Base Configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fitai-secret-key-change-in-production-2026')
    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    # Storage Locations (use writable /tmp on Vercel serverless runtime)
    UPLOAD_FOLDER = '/tmp/uploads' if IS_VERCEL else os.path.join(BASE_DIR, 'uploads')
    REPORT_FOLDER = '/tmp/reports' if IS_VERCEL else os.path.join(BASE_DIR, 'reports')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload limit

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    """Development Environment Configuration"""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Production Environment Configuration"""
    DEBUG = False
    ENV = 'production'
    SESSION_COOKIE_SECURE = True


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
