"""
BMI Record Database Model
Stores individual BMI calculation results per user.
Table is created automatically by SQLAlchemy if it does not exist.
"""

from datetime import datetime, timezone
from models import db


class BmiRecord(db.Model):
    """Stores a single BMI calculation result for a user."""
    __tablename__ = 'bmi_records'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    height_cm    = db.Column(db.Float, nullable=False)
    weight_kg    = db.Column(db.Float, nullable=False)
    age          = db.Column(db.Integer, nullable=False)
    gender       = db.Column(db.String(10), nullable=False)   # 'male' | 'female'
    bmi_value    = db.Column(db.Float, nullable=False)
    bmi_category = db.Column(db.String(30), nullable=False)
    recorded_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    # Relationship back to the User model
    user = db.relationship('User', backref=db.backref('bmi_records', lazy=True))

    def to_dict(self) -> dict:
        """Return a serialisable dictionary of this record."""
        return {
            'id':           self.id,
            'user_id':      self.user_id,
            'height_cm':    self.height_cm,
            'weight_kg':    self.weight_kg,
            'age':          self.age,
            'gender':       self.gender,
            'bmi_value':    self.bmi_value,
            'bmi_category': self.bmi_category,
            'recorded_at':  self.recorded_at.isoformat() if self.recorded_at else None,
        }

    def __repr__(self) -> str:
        return f"<BmiRecord user_id={self.user_id} bmi={self.bmi_value} category='{self.bmi_category}'>"
