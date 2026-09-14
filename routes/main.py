from datetime import datetime, timezone
from flask import Blueprint, render_template, jsonify
from sqlalchemy import text
from models import db
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def homepage():
    return render_template('index.html')

@main_bp.route('/health')
def health_check():
    try:
        db.session.execute(text('SELECT 1'))
        db.session.execute(text('SELECT id FROM users LIMIT 1'))
        db.session.execute(text('SELECT id FROM bmi_records LIMIT 1'))
        db.session.execute(text('SELECT id FROM activities LIMIT 1'))
    except Exception:
        db.session.rollback()
        return jsonify(status='unavailable', database='unavailable'), 503
    return jsonify(status='healthy', database='connected', timestamp=datetime.now(timezone.utc).isoformat())
