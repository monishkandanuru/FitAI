"""
Authentication & User Account Blueprint
Handles user registration, authentication sessions, password security, dashboard views, and module placeholders.
"""

import re
from datetime import datetime, timezone
from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
)
from models import db, User, BmiRecord, Activity
from utils.bmi import calculate
from urllib.parse import urlsplit

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    """Decorator to enforce authentication on protected endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.path))
        
        user = db.session.get(User, session['user_id'])
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
        g.user = db.session.get(User, user_id)


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
        if not full_name or len(full_name) > 100:
            errors.append("Full Name is required and must be at most 100 characters.")
        if not email:
            errors.append("Email address is required.")
        elif len(email) > 120 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            errors.append("Please provide a valid email address.")
            
        if not password:
            errors.append("Password is required.")
        elif not 8 <= len(password) <= 128:
            errors.append("Password must contain 8–128 characters.")
            
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
            session.clear()
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
            if next_page and next_page.startswith('/') and not next_page.startswith('//') and not urlsplit(next_page).netloc and '\\' not in next_page and not any(ord(c) < 32 for c in next_page):
                return redirect(next_page)
            return redirect(url_for('auth.dashboard'))
        else:
            flash("Invalid email or password. Please check your credentials.", "danger")
            return render_template('auth/login.html', email=email)

    return render_template('auth/login.html')


@auth_bp.route('/logout', methods=['POST'])
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
    
    latest = BmiRecord.query.filter_by(user_id=g.user.id).order_by(BmiRecord.recorded_at.desc(), BmiRecord.id.desc()).first()
    today = datetime.now(timezone.utc).date()
    activities = Activity.query.filter_by(user_id=g.user.id, day=today).all()
    return render_template('dashboard.html', user=g.user, greeting=greeting,
        today_date=today_date, latest=latest,
        minutes=sum(a.amount for a in activities if a.kind == 'workout'),
        calories=sum(a.amount for a in activities if a.kind == 'diet'),
        records=BmiRecord.query.filter_by(user_id=g.user.id).count())


@auth_bp.route('/profile')
@login_required
def profile():
    """Render user profile page."""
    return render_template('profile.html', user=g.user)


@auth_bp.route('/bmi', methods=['GET', 'POST'])
@login_required
def bmi():
    result = None
    if request.method == 'POST':
        try:
            result = calculate(request.form)
        except ValueError as exc:
            flash(str(exc), 'danger')
    values = {k: request.form.get(k, '') for k in ('height_cm', 'weight_kg', 'age', 'gender')}
    return render_template('bmi.html', result=result, **values)

@auth_bp.route('/bmi/save', methods=['POST'])
@login_required
def bmi_save():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(success=False, error='Expected a JSON object.'), 400
    try:
        result = calculate(data)
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    result.pop('category_class')
    record = BmiRecord(user_id=g.user.id, **result)
    try:
        db.session.add(record)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(success=False, error='Unable to save right now. Please try again.'), 503
    return jsonify(success=True, record_id=record.id, message='BMI result saved successfully!')


def activity_page(kind):
    title = 'Workout Journal' if kind == 'workout' else 'Meal Journal'
    unit = 'minutes' if kind == 'workout' else 'kcal'
    if request.method == 'POST':
        label = request.form.get('label', '').strip()
        try:
            amount = int(request.form.get('amount', ''))
            day = datetime.strptime(request.form.get('day', ''), '%Y-%m-%d').date()
            if not label or len(label) > 160 or not 1 <= amount <= (1440 if kind == 'workout' else 10000):
                raise ValueError
            if day > datetime.now(timezone.utc).date():
                raise ValueError
        except (ValueError, TypeError):
            flash('Enter a description, a valid amount, and a date no later than today.', 'danger')
        else:
            db.session.add(Activity(user_id=g.user.id, kind=kind, label=label, amount=amount, day=day))
            db.session.commit()
            flash('Entry saved.', 'success')
            return redirect(url_for('auth.' + kind))
    entries = Activity.query.filter_by(user_id=g.user.id, kind=kind).order_by(Activity.day.desc(), Activity.id.desc()).limit(100).all()
    return render_template('journal.html', title=title, unit=unit, entries=entries,
                           today=datetime.now(timezone.utc).date().isoformat(), kind=kind)

@auth_bp.route('/workout', methods=['GET', 'POST'])
@login_required
def workout():
    return activity_page('workout')

@auth_bp.route('/diet', methods=['GET', 'POST'])
@login_required
def diet():
    return activity_page('diet')

@auth_bp.route('/progress')
@login_required
def progress():
    records = BmiRecord.query.filter_by(user_id=g.user.id).order_by(BmiRecord.recorded_at.desc(), BmiRecord.id.desc()).limit(100).all()
    return render_template('progress.html', records=records)

@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form.get('full_name', '').strip()
        password = request.form.get('new_password', '')
        if not g.user.check_password(request.form.get('current_password', '')):
            flash('Current password is incorrect.', 'danger')
        elif not name or len(name) > 100:
            flash('Enter a name of 1–100 characters.', 'danger')
        elif password and (not 8 <= len(password) <= 128 or password != request.form.get('confirm_password')):
            flash('New passwords must match and contain 8–128 characters.', 'danger')
        else:
            g.user.full_name = name
            if password:
                g.user.set_password(password)
            db.session.commit()
            flash('Account updated.', 'success')
            return redirect(url_for('auth.settings'))
    return render_template('settings.html', user=g.user)
