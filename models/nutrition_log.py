"""
Nutrition Log Database Model
Stores daily calorie and macro intake records for user progress tracking.
"""

from datetime import datetime
from models import db


class NutritionLog(db.Model):
    """Stores daily calorie and protein/macro intake records for a user."""
    __tablename__ = 'nutrition_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    calories_consumed = db.Column(db.Integer, nullable=False)
    protein_grams = db.Column(db.Float, nullable=False, default=0.0)
    carbs_grams = db.Column(db.Float, nullable=False, default=0.0)
    fats_grams = db.Column(db.Float, nullable=False, default=0.0)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('nutrition_logs', lazy=True))

    def to_dict(self) -> dict:
        """Return dictionary representation of nutrition log."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'calories_consumed': self.calories_consumed,
            'protein_grams': self.protein_grams,
            'carbs_grams': self.carbs_grams,
            'fats_grams': self.fats_grams,
            'logged_at': self.logged_at.isoformat() if self.logged_at else None
        }

    def __repr__(self) -> str:
        return f"<NutritionLog user_id={self.user_id} calories={self.calories_consumed}>"
