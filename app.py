"""
FitAI Application Entrypoint
Initializes and configures the Flask application with SQLAlchemy and Blueprints.
"""

import os
from datetime import timedelta
from flask import Flask, render_template, jsonify, g, redirect, url_for, request
from config import config_by_name, DevelopmentConfig
from models import db
from flask_wtf.csrf import CSRFProtect, CSRFError


def create_app(config_class=DevelopmentConfig):
    """Application factory for FitAI."""
    app = Flask(__name__)
    
    # Load configuration
    if isinstance(config_class, str):
        app.config.from_object(config_by_name[config_class])
    else:
        app.config.from_object(config_class)

    # Session Lifetime Configuration
    app.permanent_session_lifetime = timedelta(days=30)
        
    if app.config.get('ENV') == 'production':
        if not os.getenv('SECRET_KEY') or len(os.environ['SECRET_KEY']) < 32:
            raise RuntimeError('Production requires a SECRET_KEY of at least 32 characters.')
        if not os.getenv('DATABASE_URL'):
            raise RuntimeError('Production requires DATABASE_URL.')
        if os.getenv('VERCEL') and app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:'):
            raise RuntimeError('Vercel requires a persistent external database, such as PostgreSQL.')
    CSRFProtect(app)

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

    @app.route('/logout', methods=['POST'])
    def alias_logout():
        return redirect(url_for('auth.logout'), code=307)

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
    if app.config.get('AUTO_CREATE_DB'):
        with app.app_context():
            db.create_all()

    @app.cli.command('init-db')
    def init_db():
        """Create missing tables without deleting existing data."""
        db.create_all()

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if g.get('user') or request.path.startswith('/auth'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        if request.is_json:
            return jsonify(success=False, error='Session expired. Refresh the page and try again.'), 400
        return render_template('error.html', message='Session expired. Refresh the form and try again.'), 400

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
        db.session.rollback()
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred in the FitAI backend service."
        }), 500

    return app


# Application instance for gunicorn / flask CLI
app = create_app(os.environ.get('FLASK_ENV', 'production' if os.getenv('VERCEL') else 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', True))
