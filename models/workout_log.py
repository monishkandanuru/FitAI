"""
Workout Log Database Model
Stores completed workout session records for user progress tracking.
"""

from datetime import datetime
from models import db


class WorkoutLog(db.Model):
    """Stores completed workout session records for a user."""
    __tablename__ = 'workout_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    workout_title = db.Column(db.String(100), nullable=False)
    completed_exercises = db.Column(db.Integer, nullable=False, default=1)
    duration_mins = db.Column(db.Integer, nullable=False, default=30)
    form_score = db.Column(db.Integer, nullable=True)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('workout_logs', lazy=True))

    def to_dict(self) -> dict:
        """Return dictionary representation of workout log."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'workout_title': self.workout_title,
            'completed_exercises': self.completed_exercises,
            'duration_mins': self.duration_mins,
            'form_score': self.form_score,
            'logged_at': self.logged_at.isoformat() if self.logged_at else None
        }

    def __repr__(self) -> str:
        return f"<WorkoutLog user_id={self.user_id} title='{self.workout_title}'>"
