"""
FitAI Models Package
Initializes Flask-SQLAlchemy instance and exposes data models.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.bmi_record import BmiRecord

__all__ = ['db', 'User', 'BmiRecord']

from models.activity import Activity
