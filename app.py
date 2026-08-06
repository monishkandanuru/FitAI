"""
FitAI Application Entrypoint
Initializes and configures the Flask application with SQLAlchemy and Blueprints.
"""

import os
from datetime import timedelta
from flask import Flask, render_template, jsonify, g, redirect, url_for
from config import config_by_name, DevelopmentConfig
from models import db


def create_app(config_class=DevelopmentConfig):
    """Application factory for FitAI."""
    app = Flask(__name__)
    
    # Load configuration
    if isinstance(config_class, str):
        app.config.from_object(config_by_name.get(config_class, DevelopmentConfig))
    else:
        app.config.from_object(config_class)

    # Session Lifetime Configuration
    app.permanent_session_lifetime = timedelta(days=30)
        
    # Ensure required runtime directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)

    # Initialize SQLAlchemy database engine
    db.init_app(app)

    # Register Blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # Convenience Route Aliases
    @app.route('/login')
    def alias_login():
        return redirect(url_for('auth.login'))

    @app.route('/register')
    def alias_register():
        return redirect(url_for('auth.register'))

    @app.route('/logout')
    def alias_logout():
        return redirect(url_for('auth.logout'))

    @app.route('/dashboard')
    def alias_dashboard():
        return redirect(url_for('auth.dashboard'))

    @app.route('/profile')
    def alias_profile():
        return redirect(url_for('auth.profile'))

    @app.route('/bmi')
    def alias_bmi():
        return redirect(url_for('auth.bmi'))

    @app.route('/workout')
    def alias_workout():
        return redirect(url_for('auth.workout'))

    @app.route('/diet')
    def alias_diet():
        return redirect(url_for('auth.diet'))

    @app.route('/progress')
    def alias_progress():
        return redirect(url_for('auth.progress'))

    @app.route('/settings')
    def alias_settings():
        return redirect(url_for('auth.settings'))

    # Inject current_user into all templates automatically
    @app.context_processor
    def inject_user():
        return dict(current_user=g.get('user', None))

    # Auto-create SQLite database tables if missing
    with app.app_context():
        db.create_all()

    # Register Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('base.html', page_title="Page Not Found", content_override="""
            <div class="container error-container text-center py-5">
                <div class="glass-card error-card" style="padding: 3rem 2rem; max-width: 500px; margin: 3rem auto;">
                    <span class="error-badge" style="font-size: 2.5rem; font-weight: 800; color: #10b981;">404</span>
                    <h2 style="font-family: var(--font-heading); margin: 0.5rem 0;">Page Not Found</h2>
                    <p style="color: var(--text-muted);">The requested page or resource could not be located.</p>
                    <a href="/" class="btn btn-primary mt-3">Return to FitAI Dashboard</a>
                </div>
            </div>
        """), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred in the FitAI backend service."
        }), 500

    return app


# Application instance for gunicorn / flask CLI
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', True))
