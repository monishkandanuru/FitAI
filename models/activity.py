from datetime import datetime, timezone
from models import db

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    kind = db.Column(db.String(10), nullable=False)
    label = db.Column(db.String(160), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
