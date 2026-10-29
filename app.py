"""
FitAI Application Entrypoint
Initializes and configures the Flask application with SQLAlchemy, Blueprints, and Vercel/WSGI readiness.
"""

import os
from datetime import timedelta
from flask import Flask, render_template, jsonify, g, redirect, url_for
from config import config_by_name, DevelopmentConfig
from models import db, seed_initial_exercises


def create_app(config_class=None):
    """Application factory for FitAI."""
    app = Flask(__name__)

    if config_class is None:
        env_name = os.environ.get('FLASK_ENV') or (
            'production' if os.environ.get('VERCEL') else 'development'
        )
        config_class = config_by_name.get(env_name, DevelopmentConfig)

    # Load configuration
    if isinstance(config_class, str):
        app.config.from_object(config_by_name.get(config_class, DevelopmentConfig))
    else:
        app.config.from_object(config_class)

    # Session Lifetime Configuration
    app.permanent_session_lifetime = timedelta(days=30)

    # Ensure required runtime directories exist (guarded for read-only serverless environments)
    for folder_key in ('UPLOAD_FOLDER', 'REPORT_FOLDER'):
        folder_path = app.config.get(folder_key)
        if folder_path:
            try:
                os.makedirs(folder_path, exist_ok=True)
            except OSError:
                pass

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

    @app.route('/workout/camera')
    def alias_workout_camera():
        return redirect(url_for('auth.workout_camera'))

    @app.route('/body-assessment')
    def alias_body_assessment():
        return redirect(url_for('auth.body_assessment'))

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

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        return response

    # Auto-create database tables if missing and seed initial dataset
    with app.app_context():
        try:
            db.create_all()
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE workout_logs ADD COLUMN form_score INTEGER"))
                    conn.commit()
            except Exception:
                pass
            seed_initial_exercises()
        except Exception as exc:
            app.logger.warning(f"Database initialization warning: {exc}")

    @app.cli.command("init-db")
    def init_db_command():
        """Explicit CLI command to initialize database tables and seed exercises."""
        db.create_all()
        seed_initial_exercises()
        print("Initialized FitAI database and seeded exercises.")

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


# Application instance for Vercel / gunicorn / flask CLI
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', True))
