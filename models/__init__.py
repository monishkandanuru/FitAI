"""
FitAI Models Package
Initializes Flask-SQLAlchemy instance and exposes data models.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.bmi_record import BmiRecord
from models.exercise import Exercise, seed_initial_exercises
from models.workout_log import WorkoutLog
from models.nutrition_log import NutritionLog
from models.body_assessment import BodyAssessment

__all__ = [
    'db',
    'User',
    'BmiRecord',
    'Exercise',
    'seed_initial_exercises',
    'WorkoutLog',
    'NutritionLog',
    'BodyAssessment'
]
