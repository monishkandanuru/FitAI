"""
Authentication & User Account Blueprint
Handles user registration, authentication sessions, password security, dashboard views,
BMI calculation, workout planning, live camera session logging, body assessments,
nutrition/macro intelligence, progress analytics, and account settings.
"""

import re
from datetime import datetime
from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
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

        new_user = User(full_name=full_name, email=email)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            
            session['user_id'] = new_user.id
            flash(f"Welcome to FitAI, {new_user.full_name}! Your account was created successfully.", "success")
            return redirect(url_for('auth.dashboard'))
        except Exception:
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
            if next_page and next_page.startswith('/') and not next_page.startswith('//'):
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
    """Render protected user dashboard with live database metrics & personalized recommendations."""
    from models import BmiRecord, WorkoutLog, NutritionLog, BodyAssessment
    from utils.nutrition_calculator import calculate_nutrition_targets
    from utils.recommendations import generate_personalized_recommendations

    greeting = get_time_greeting()
    today_date = datetime.now().strftime('%A, %B %d, %Y')

    latest_bmi = BmiRecord.query.filter_by(user_id=g.user.id).order_by(BmiRecord.recorded_at.desc()).first()
    workout_logs = WorkoutLog.query.filter_by(user_id=g.user.id).order_by(WorkoutLog.logged_at.desc()).all()
    nutrition_logs = NutritionLog.query.filter_by(user_id=g.user.id).order_by(NutritionLog.logged_at.desc()).all()
    latest_assessment = BodyAssessment.query.filter_by(user_id=g.user.id).order_by(BodyAssessment.assessed_at.desc()).first()

    # Calculate personalized nutrition targets from latest BMI or sensible defaults
    w_kg = latest_bmi.weight_kg if latest_bmi else 70.0
    h_cm = latest_bmi.height_cm if latest_bmi else 175.0
    u_age = latest_bmi.age if latest_bmi else 25
    u_gender = latest_bmi.gender if latest_bmi else 'male'

    nut_plan = calculate_nutrition_targets(
        weight_kg=w_kg,
        height_cm=h_cm,
        age=u_age,
        gender=u_gender,
        activity_level='Moderately Active',
        goal='Maintenance'
    )
    target_cals = nut_plan['target_calories']
    target_prot = nut_plan['macros']['protein']['grams']

    latest_nut = nutrition_logs[0] if nutrition_logs else None
    consumed_cals = latest_nut.calories_consumed if latest_nut else 0
    cals_pct = min(100, round((consumed_cals / target_cals) * 100)) if target_cals else 0

    total_workout_mins = sum(w.duration_mins for w in workout_logs)
    scored_workouts = [w for w in workout_logs if w.form_score is not None]
    avg_form = (
        round(sum(w.form_score for w in scored_workouts) / len(scored_workouts))
        if scored_workouts else None
    )

    if latest_bmi:
        h_m = latest_bmi.height_cm / 100.0
        ideal_min = round(18.5 * (h_m ** 2), 1)
        ideal_max = round(24.9 * (h_m ** 2), 1)
        bmi_display = latest_bmi.bmi_value
        bmi_cat_display = latest_bmi.bmi_category
        bmi_sub_display = f"Healthy range: {ideal_min}–{ideal_max} kg"
        weight_display = f"{latest_bmi.weight_kg} kg"
        weight_sub_display = f"Height: {latest_bmi.height_cm} cm"
    else:
        bmi_display = "--"
        bmi_cat_display = "Unlogged"
        bmi_sub_display = "Use BMI Calculator to log baseline"
        weight_display = "-- kg"
        weight_sub_display = "No weight record saved yet"

    stats = {
        'bmi': bmi_display,
        'bmi_category': bmi_cat_display,
        'bmi_sub': bmi_sub_display,
        'weight': weight_display,
        'weight_sub': weight_sub_display,
        'calories_target': f"{target_cals:,} kcal",
        'calories_consumed': f"{consumed_cals:,} kcal logged" if latest_nut else "No meal logged yet",
        'calories_pct': cals_pct,
        'protein_target': target_prot,
        'workout_count': len(workout_logs),
        'workout_mins': total_workout_mins,
        'form_sub': f"Avg Camera Form Score: {avg_form}%" if avg_form is not None else "Run Camera Coach to score form"
    }

    recommendations = generate_personalized_recommendations(
        latest_bmi=latest_bmi,
        workout_logs=workout_logs,
        nutrition_logs=nutrition_logs,
        latest_assessment=latest_assessment,
        target_calories=target_cals,
        target_protein_g=target_prot
    )

    return render_template(
        'dashboard.html',
        user=g.user,
        greeting=greeting,
        today_date=today_date,
        stats=stats,
        recommendations=recommendations
    )


@auth_bp.route('/profile')
@login_required
def profile():
    """Render user profile page."""
    return render_template('profile.html', user=g.user)


@auth_bp.route('/bmi', methods=['GET', 'POST'])
@login_required
def bmi():
    """
    BMI Calculator — GET renders the form, POST computes BMI and renders result.
    """
    result = None

    if request.method == 'POST':
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
            'bmi_value':      bmi_value,
            'bmi_category':   bmi_category,
            'category_class': category_class,
            'height_cm':      height_cm,
            'weight_kg':      weight_kg,
            'age':            age,
            'gender':         gender.capitalize(),
        }

        return render_template('bmi.html',
                               height_cm=height_cm, weight_kg=weight_kg,
                               age=age, gender=gender, result=result)

    return render_template('bmi.html',
                           height_cm='', weight_kg='', age='', gender='', result=None)


@auth_bp.route('/bmi/save', methods=['POST'])
@login_required
def bmi_save():
    """
    Save a calculated BMI result into the bmi_records table, recomputing BMI server-side.
    """
    from models import BmiRecord

    data = request.get_json(silent=True) or {}

    try:
        height_cm = float(data.get('height_cm', 0))
        weight_kg = float(data.get('weight_kg', 0))
        age       = int(data.get('age', 0))
        gender    = str(data.get('gender', '')).strip().lower()
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid payload.'}), 400

    if not (0 < height_cm <= 300 and 0 < weight_kg <= 600 and 0 < age <= 120 and gender in ('male', 'female')):
        return jsonify({'success': False, 'error': 'Incomplete or out-of-range biometric data.'}), 400

    height_m = height_cm / 100.0
    raw_bmi = weight_kg / (height_m ** 2)
    bmi_value = round(raw_bmi, 1)

    if raw_bmi < 18.5:
        bmi_category = "Underweight"
    elif raw_bmi < 25:
        bmi_category = "Normal Weight"
    elif raw_bmi < 30:
        bmi_category = "Overweight"
    else:
        bmi_category = "Obese"

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
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Could not save BMI record.'}), 500


@auth_bp.route('/workout', methods=['GET', 'POST'])
@login_required
def workout():
    """Render Workout Planner page and generate custom training routine."""
    from utils.workout_generator import generate_workout_plan

    if request.method == 'POST':
        goal = request.form.get('goal', 'Muscle Gain').strip()
        fitness_level = request.form.get('fitness_level', 'Beginner').strip()
        focus = request.form.get('focus', 'Full Body').strip()
    else:
        goal = request.args.get('goal', 'Muscle Gain').strip()
        fitness_level = request.args.get('fitness_level', 'Beginner').strip()
        focus = request.args.get('focus', 'Full Body').strip()

    workout_plan = generate_workout_plan(goal=goal, fitness_level=fitness_level, focus=focus)

    return render_template(
        'workout.html',
        workout_plan=workout_plan,
        selected_goal=goal,
        selected_level=fitness_level,
        selected_focus=focus
    )


@auth_bp.route('/workout/camera')
@login_required
def workout_camera():
    """Render Workout Live Motion Tracking Camera page with latest user weight."""
    from models import BmiRecord

    latest_bmi = BmiRecord.query.filter_by(user_id=g.user.id).order_by(BmiRecord.recorded_at.desc()).first()
    latest_weight = latest_bmi.weight_kg if latest_bmi else 70.0

    return render_template('workout_camera.html', latest_weight=latest_weight)


@auth_bp.route('/workout/camera/save_session', methods=['POST'])
@login_required
def save_camera_session():
    """Save a completed camera workout session via JSON POST. Returns JSON response."""
    from models import db, WorkoutLog

    data = request.get_json(silent=True) or {}

    try:
        exercise_name   = str(data.get('exercise_name', 'Camera Workout')).strip()[:100]
        total_reps      = int(data.get('total_reps', 0))
        duration_secs   = int(data.get('duration_secs', 0))
        calories_burned = float(data.get('calories_burned', 0.0))
        form_score_raw  = data.get('form_score')
        form_score      = int(form_score_raw) if form_score_raw is not None else None
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid session payload.'}), 400

    duration_mins = max(1, round(duration_secs / 60))
    title = f"{exercise_name} – {total_reps} reps ({calories_burned:.1f} kcal)"

    log = WorkoutLog(
        user_id=g.user.id,
        workout_title=title[:100],
        completed_exercises=max(1, total_reps),
        duration_mins=duration_mins,
        form_score=form_score
    )

    try:
        db.session.add(log)
        db.session.commit()
        return jsonify({'success': True, 'log_id': log.id,
                        'message': f'Session saved: {title}'})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to save camera workout session.'}), 500


@auth_bp.route('/body_assessment')
@login_required
def body_assessment():
    """Render Stage 3 Pose-Based Body Proportion & Posture Assessment page."""
    from models import BmiRecord, BodyAssessment

    latest_bmi = BmiRecord.query.filter_by(user_id=g.user.id).order_by(BmiRecord.recorded_at.desc()).first()
    default_height = latest_bmi.height_cm if latest_bmi else 175.0
    assessments = BodyAssessment.query.filter_by(user_id=g.user.id).order_by(BodyAssessment.assessed_at.desc()).all()

    return render_template(
        'body_assessment.html',
        default_height=default_height,
        assessments=assessments
    )


@auth_bp.route('/body_assessment/save', methods=['POST'])
@login_required
def save_body_assessment():
    """Save a calibrated Body Assessment record."""
    from models import db, BodyAssessment

    try:
        estimated_height_cm = float(request.form.get('estimated_height_cm', 175.0))
        shoulder_hip_ratio = float(request.form.get('shoulder_hip_ratio', 1.30))
        torso_leg_ratio = float(request.form.get('torso_leg_ratio', 0.68))
        posture_score = int(request.form.get('posture_score', 88))
        symmetry_score = int(request.form.get('symmetry_score', 90))
    except (ValueError, TypeError):
        flash("Invalid numeric values for body assessment.", "danger")
        return redirect(url_for('auth.body_assessment'))

    frame_category = request.form.get('frame_category', 'Balanced Athletic').strip()[:50] or 'Balanced Athletic'
    recommendation_summary = request.form.get('recommendation_summary', '').strip()[:300]

    record = BodyAssessment(
        user_id=g.user.id,
        estimated_height_cm=max(100.0, min(250.0, estimated_height_cm)),
        shoulder_hip_ratio=round(max(0.5, min(2.5, shoulder_hip_ratio)), 2),
        torso_leg_ratio=round(max(0.3, min(1.5, torso_leg_ratio)), 2),
        posture_score=max(1, min(100, posture_score)),
        symmetry_score=max(1, min(100, symmetry_score)),
        frame_category=frame_category,
        recommendation_summary=recommendation_summary
    )

    try:
        db.session.add(record)
        db.session.commit()
        flash("Body assessment saved to your history!", "success")
    except Exception:
        db.session.rollback()
        flash("Could not save body assessment.", "danger")

    return redirect(url_for('auth.body_assessment'))


@auth_bp.route('/diet', methods=['GET', 'POST'])
@login_required
def diet():
    """Render Diet & Nutrition Planner page and calculate BMR, TDEE, and macro targets."""
    from models import BmiRecord
    from utils.nutrition_calculator import calculate_nutrition_targets

    latest_bmi = BmiRecord.query.filter_by(user_id=g.user.id).order_by(BmiRecord.recorded_at.desc()).first()

    default_height = latest_bmi.height_cm if latest_bmi else 175.0
    default_weight = latest_bmi.weight_kg if latest_bmi else 70.0
    default_age = latest_bmi.age if latest_bmi else 25
    default_gender = latest_bmi.gender.capitalize() if latest_bmi else 'Male'

    if request.method == 'POST':
        try:
            height_cm = float(request.form.get('height_cm', default_height))
        except (ValueError, TypeError):
            height_cm = default_height
        try:
            weight_kg = float(request.form.get('weight_kg', default_weight))
        except (ValueError, TypeError):
            weight_kg = default_weight
        try:
            age = int(request.form.get('age', default_age))
        except (ValueError, TypeError):
            age = default_age

        gender = request.form.get('gender', default_gender).strip()
        activity_level = request.form.get('activity_level', 'Moderately Active').strip()
        goal = request.form.get('goal', 'Maintenance').strip()
    else:
        height_cm = default_height
        weight_kg = default_weight
        age = default_age
        gender = default_gender
        activity_level = 'Moderately Active'
        goal = 'Maintenance'

    nutrition_plan = calculate_nutrition_targets(
        weight_kg=weight_kg,
        height_cm=height_cm,
        age=age,
        gender=gender,
        activity_level=activity_level,
        goal=goal
    )

    return render_template(
        'diet.html',
        nutrition_plan=nutrition_plan,
        height_cm=height_cm,
        weight_kg=weight_kg,
        age=age,
        gender=gender,
        activity_level=activity_level,
        goal=goal
    )


@auth_bp.route('/progress')
@login_required
def progress():
    """Render Progress Tracking page displaying weight/BMI, workout, and nutrition history with analytics charts."""
    from models import BmiRecord, WorkoutLog, NutritionLog

    bmi_history = BmiRecord.query.filter_by(user_id=g.user.id).order_by(BmiRecord.recorded_at.desc()).all()
    workout_history = WorkoutLog.query.filter_by(user_id=g.user.id).order_by(WorkoutLog.logged_at.desc()).all()
    nutrition_history = NutritionLog.query.filter_by(user_id=g.user.id).order_by(NutritionLog.logged_at.desc()).all()

    bmi_chrono = list(reversed(bmi_history))
    workout_chrono = list(reversed(workout_history))
    nutrition_chrono = list(reversed(nutrition_history))

    chart_data = {
        'weight_labels': [b.recorded_at.strftime('%b %d') if b.recorded_at else 'N/A' for b in bmi_chrono],
        'weight_values': [b.weight_kg for b in bmi_chrono],
        'bmi_values': [b.bmi_value for b in bmi_chrono],
        'nutrition_labels': [n.logged_at.strftime('%b %d') if n.logged_at else 'N/A' for n in nutrition_chrono],
        'calories_values': [n.calories_consumed for n in nutrition_chrono],
        'protein_values': [n.protein_grams for n in nutrition_chrono],
        'workout_labels': [w.logged_at.strftime('%b %d') if w.logged_at else 'N/A' for w in workout_chrono],
        'workout_counts': [w.completed_exercises for w in workout_chrono],
        'workout_durations': [w.duration_mins for w in workout_chrono]
    }

    return render_template(
        'progress.html',
        bmi_history=bmi_history,
        workout_history=workout_history,
        nutrition_history=nutrition_history,
        chart_data=chart_data
    )


@auth_bp.route('/progress/log_workout', methods=['POST'])
@login_required
def log_workout():
    """Log a completed workout session."""
    from models import db, WorkoutLog

    workout_title = request.form.get('workout_title', 'General Workout').strip()[:100] or 'General Workout'
    try:
        completed_exercises = int(request.form.get('completed_exercises', 1))
        duration_mins = int(request.form.get('duration_mins', 30))
    except (ValueError, TypeError):
        flash("Invalid workout numbers provided.", "danger")
        return redirect(url_for('auth.progress'))

    if completed_exercises <= 0 or duration_mins <= 0 or duration_mins > 600:
        flash("Workout exercises and duration must be positive numbers.", "danger")
        return redirect(url_for('auth.progress'))

    log = WorkoutLog(
        user_id=g.user.id,
        workout_title=workout_title,
        completed_exercises=completed_exercises,
        duration_mins=duration_mins
    )

    try:
        db.session.add(log)
        db.session.commit()
        flash("Workout session logged successfully!", "success")
    except Exception:
        db.session.rollback()
        flash("Failed to log workout session.", "danger")

    return redirect(url_for('auth.progress'))


@auth_bp.route('/progress/log_nutrition', methods=['POST'])
@login_required
def log_nutrition():
    """Log daily calorie and macro intake."""
    from models import db, NutritionLog

    try:
        calories_consumed = int(request.form.get('calories_consumed', 2000))
        protein_grams = float(request.form.get('protein_grams', 0.0))
        carbs_grams = float(request.form.get('carbs_grams', 0.0) or 0.0)
        fats_grams = float(request.form.get('fats_grams', 0.0) or 0.0)
    except (ValueError, TypeError):
        flash("Invalid nutrition values.", "danger")
        return redirect(url_for('auth.progress'))

    if calories_consumed <= 0 or calories_consumed > 15000 or protein_grams < 0 or carbs_grams < 0 or fats_grams < 0:
        flash("Please enter realistic positive calorie and macro amounts.", "danger")
        return redirect(url_for('auth.progress'))

    log = NutritionLog(
        user_id=g.user.id,
        calories_consumed=calories_consumed,
        protein_grams=protein_grams,
        carbs_grams=carbs_grams,
        fats_grams=fats_grams
    )

    try:
        db.session.add(log)
        db.session.commit()
        flash("Daily nutrition logged successfully!", "success")
    except Exception:
        db.session.rollback()
        flash("Failed to log nutrition intake.", "danger")

    return redirect(url_for('auth.progress'))


@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Render and process Account Settings (profile name update & password change)."""
    from models import BmiRecord, WorkoutLog, NutritionLog, BodyAssessment

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_new_password = request.form.get('confirm_new_password', '')

        errors = []
        if not full_name or len(full_name) > 100:
            errors.append("Please provide a valid full name (1–100 characters).")
        if not current_password or not g.user.check_password(current_password):
            errors.append("Current password is incorrect.")
        if new_password:
            if len(new_password) < 8:
                errors.append("New password must be at least 8 characters long.")
            elif new_password != confirm_new_password:
                errors.append("New password and confirmation do not match.")

        if errors:
            for err in errors:
                flash(err, "danger")
        else:
            g.user.full_name = full_name
            if new_password:
                g.user.set_password(new_password)
            try:
                db.session.commit()
                flash("Account settings updated successfully!", "success")
                return redirect(url_for('auth.settings'))
            except Exception:
                db.session.rollback()
                flash("Failed to update account settings.", "danger")

    counts = {
        'bmi_count': BmiRecord.query.filter_by(user_id=g.user.id).count(),
        'workout_count': WorkoutLog.query.filter_by(user_id=g.user.id).count(),
        'nutrition_count': NutritionLog.query.filter_by(user_id=g.user.id).count(),
        'assessment_count': BodyAssessment.query.filter_by(user_id=g.user.id).count(),
    }

    return render_template('settings.html', user=g.user, counts=counts)
