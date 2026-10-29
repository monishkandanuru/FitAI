"""
Body Assessment Database Model
Stores pose-based body proportion, posture symmetry, and calibrated height estimations per user.
Note: Camera-based body measurements are visual estimates and not medical diagnoses.
"""

from datetime import datetime
from models import db


class BodyAssessment(db.Model):
    """Stores a pose-based body proportion and posture assessment record for a user."""
    __tablename__ = 'body_assessments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    estimated_height_cm = db.Column(db.Float, nullable=False)
    shoulder_hip_ratio = db.Column(db.Float, nullable=False)
    torso_leg_ratio = db.Column(db.Float, nullable=False)
    posture_score = db.Column(db.Integer, nullable=False, default=85)
    symmetry_score = db.Column(db.Integer, nullable=False, default=90)
    frame_category = db.Column(db.String(50), nullable=False, default='Balanced Athletic')
    recommendation_summary = db.Column(db.String(300), nullable=True)
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('body_assessments', lazy=True))

    def to_dict(self) -> dict:
        """Return serialisable dictionary of this body assessment."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'estimated_height_cm': self.estimated_height_cm,
            'shoulder_hip_ratio': self.shoulder_hip_ratio,
            'torso_leg_ratio': self.torso_leg_ratio,
            'posture_score': self.posture_score,
            'symmetry_score': self.symmetry_score,
            'frame_category': self.frame_category,
            'recommendation_summary': self.recommendation_summary,
            'assessed_at': self.assessed_at.isoformat() if self.assessed_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<BodyAssessment user_id={self.user_id} "
            f"height_est={self.estimated_height_cm}cm posture={self.posture_score}>"
        )
