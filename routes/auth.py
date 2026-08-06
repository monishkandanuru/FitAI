"""
Authentication & User Account Blueprint
Handles user registration, authentication sessions, password security, dashboard views, and module placeholders.
"""

import re
from datetime import datetime
from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session, g
)
from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    """Decorator to enforce authentication on protected endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            flash("Session expired or user not found. Please log in again.", "warning")
            return redirect(url_for('auth.login'))
            
        g.user = user
        return f(*args, **kwargs)
    return decorated_function


def get_time_greeting():
    """Returns a time-sensitive greeting string based on current hour."""
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"


@auth_bp.before_app_request
def load_logged_in_user():
    """Load current user into Flask g object before each request if logged in."""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new user account registration."""
    if g.user:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Server-side validations
        errors = []
        if not full_name:
            errors.append("Full Name is required.")
        if not email:
            errors.append("Email address is required.")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Please provide a valid email address.")
            
        if not password:
            errors.append("Password is required.")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
            
        if password != confirm_password:
            errors.append("Password and Confirm Password do not match.")

        # Check for existing email in database
        if not errors:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                errors.append("An account with this email address already exists.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                'auth/register.html',
                full_name=full_name,
                email=email
            )

        # Create new user record
        new_user = User(full_name=full_name, email=email)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Automatically log in user after registration
            session['user_id'] = new_user.id
            flash(f"Welcome to FitAI, {new_user.full_name}! Your account was created successfully.", "success")
            return redirect(url_for('auth.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while creating your account. Please try again.", "danger")
            return render_template('auth/register.html', full_name=full_name, email=email)

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle existing user login authentication."""
    if g.user:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('auth/login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            
            if remember_me:
                session.permanent = True

            flash(f"Welcome back, {user.full_name}!", "success")
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('auth.dashboard'))
        else:
            flash("Invalid email or password. Please check your credentials.", "danger")
            return render_template('auth/login.html', email=email)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Clear session data and log out current user."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """Render protected user dashboard with metrics & progress charts."""
    greeting = get_time_greeting()
    today_date = datetime.now().strftime('%A, %B %d, %Y')
    
    # Realistic sample metrics dictionary
    stats = {
        'bmi': 22.6,
        'bmi_category': 'Normal Weight',
        'weight': '68 kg',
        'calories_target': '2,300 kcal',
        'calories_consumed': '1,450 kcal',
        'water_current': '2.5 L',
        'water_target': '3.0 L',
        'water_percentage': 83
    }
    
    return render_template(
        'dashboard.html',
        user=g.user,
        greeting=greeting,
        today_date=today_date,
        stats=stats
    )


@auth_bp.route('/profile')
@login_required
def profile():
    """Render user profile page."""
    return render_template('profile.html', user=g.user)


# Placeholder Module Endpoints
@auth_bp.route('/bmi', methods=['GET', 'POST'])
@login_required
def bmi():
    """
    BMI Calculator — GET renders the form, POST computes BMI and saves the result.
    The bmi_records table is created automatically by db.create_all() in app.py.
    """
    from models import BmiRecord

    result = None   # Holds computed BMI data after a POST

    if request.method == 'POST':
        # ── Collect & validate form inputs ──────────────────────────────────
        errors = []

        try:
            height_cm = float(request.form.get('height_cm', 0))
        except (ValueError, TypeError):
            height_cm = 0
        try:
            weight_kg = float(request.form.get('weight_kg', 0))
        except (ValueError, TypeError):
            weight_kg = 0
        try:
            age = int(request.form.get('age', 0))
        except (ValueError, TypeError):
            age = 0

        gender = request.form.get('gender', '').strip().lower()

        if height_cm <= 0 or height_cm > 300:
            errors.append("Height must be between 1 and 300 cm.")
        if weight_kg <= 0 or weight_kg > 600:
            errors.append("Weight must be between 1 and 600 kg.")
        if age <= 0 or age > 120:
            errors.append("Age must be between 1 and 120.")
        if gender not in ('male', 'female'):
            errors.append("Please select a valid gender.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template('bmi.html',
                                   height_cm=height_cm, weight_kg=weight_kg,
                                   age=age, gender=gender, result=None)

        # ── Compute BMI ──────────────────────────────────────────────────────
        height_m = height_cm / 100.0
        bmi_value = round(weight_kg / (height_m ** 2), 1)

        if bmi_value < 18.5:
            bmi_category = "Underweight"
            category_class = "bmi-underweight"
        elif bmi_value < 25:
            bmi_category = "Normal Weight"
            category_class = "bmi-normal"
        elif bmi_value < 30:
            bmi_category = "Overweight"
            category_class = "bmi-overweight"
        else:
            bmi_category = "Obese"
            category_class = "bmi-obese"

        result = {
            'bmi_value':     bmi_value,
            'bmi_category':  bmi_category,
            'category_class': category_class,
            'height_cm':     height_cm,
            'weight_kg':     weight_kg,
            'age':           age,
            'gender':        gender.capitalize(),
        }

        return render_template('bmi.html',
                               height_cm=height_cm, weight_kg=weight_kg,
                               age=age, gender=gender, result=result)

    # ── GET — render blank calculator ────────────────────────────────────────
    return render_template('bmi.html',
                           height_cm='', weight_kg='', age='', gender='', result=None)


@auth_bp.route('/bmi/save', methods=['POST'])
@login_required
def bmi_save():
    """
    Save a previously calculated BMI result into the bmi_records SQLite table.
    Expects JSON body: { height_cm, weight_kg, age, gender, bmi_value, bmi_category }
    """
    from models import BmiRecord
    from flask import request as req

    data = req.get_json(silent=True) or {}

    try:
        height_cm    = float(data.get('height_cm', 0))
        weight_kg    = float(data.get('weight_kg', 0))
        age          = int(data.get('age', 0))
        gender       = str(data.get('gender', '')).lower()
        bmi_value    = float(data.get('bmi_value', 0))
        bmi_category = str(data.get('bmi_category', ''))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid payload.'}), 400

    if not (height_cm and weight_kg and age and gender and bmi_value and bmi_category):
        return jsonify({'success': False, 'error': 'Incomplete data.'}), 400

    record = BmiRecord(
        user_id      = g.user.id,
        height_cm    = height_cm,
        weight_kg    = weight_kg,
        age          = age,
        gender       = gender,
        bmi_value    = bmi_value,
        bmi_category = bmi_category,
    )

    try:
        db.session.add(record)
        db.session.commit()
        return jsonify({'success': True, 'record_id': record.id,
                        'message': 'BMI result saved successfully!'})
    except Exception as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 500


@auth_bp.route('/workout')
@login_required
def workout():
    return render_template(
        'placeholder.html',
        module_name="Workout Planner",
        icon="🏋️‍♂️",
        tag="AI Routine Architect",
        description="Generate hyper-personalized training routines optimized for progressive overload and muscle hypertrophy."
    )


@auth_bp.route('/diet')
@login_required
def diet():
    return render_template(
        'placeholder.html',
        module_name="Diet & Nutrition Planner",
        icon="🥗",
        tag="Smart Macro Coach",
        description="Calculate metabolic caloric targets, macro splits, and customized meal recommendations."
    )


@auth_bp.route('/progress')
@login_required
def progress():
    return render_template(
        'placeholder.html',
        module_name="Progress Analytics",
        icon="📊",
        tag="Performance Intelligence",
        description="Visualize long-term strength gains, body composition changes, and workout compliance metrics."
    )


@auth_bp.route('/settings')
@login_required
def settings():
    return render_template(
        'placeholder.html',
        module_name="Account Settings",
        icon="⚙️",
        tag="Preferences & Security",
        description="Manage your account profile, notification preferences, security options, and API keys."
    )
