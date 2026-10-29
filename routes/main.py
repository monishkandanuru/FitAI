"""
Main Blueprint Routes
Contains primary web navigation endpoints and database-verified health check API.
"""

from datetime import datetime
from flask import Blueprint, render_template, jsonify, current_app
from models import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def homepage():
    """Renders the FitAI landing page."""
    return render_template(
        'index.html',
        app_name="FitAI",
        tagline="AI Powered Fitness & Nutrition Coach"
    )


@main_bp.route('/health')
def health_check():
    """System health check endpoint verifying live database connectivity."""
    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    db_backend = "PostgreSQL" if db_uri.startswith("postgresql") else "SQLite"
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({
            "status": "healthy",
            "app_name": "FitAI",
            "tagline": "AI Powered Fitness & Nutrition Coach",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "environment": current_app.config.get('ENV', 'development'),
            "database": f"{db_backend} (connected)"
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "unavailable",
            "app_name": "FitAI",
            "environment": current_app.config.get('ENV', 'development'),
            "database": f"{db_backend} (unreachable)"
        }), 503
