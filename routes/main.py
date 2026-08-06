"""
Main Blueprint Routes
Contains primary web navigation endpoints and baseline APIs.
"""

from datetime import datetime
from flask import Blueprint, render_template, jsonify, current_app

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
    """System health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "app_name": "FitAI",
        "tagline": "AI Powered Fitness & Nutrition Coach",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": current_app.config.get('ENV', 'development'),
        "database": "SQLite (configured)"
    }), 200
