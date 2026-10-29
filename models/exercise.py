"""
Exercise Database Model
Represents individual exercise definitions and initial seeded workout movement dataset.
Table is created automatically by SQLAlchemy if it does not exist.
"""

from datetime import datetime
from models import db


class Exercise(db.Model):
    """Exercise data model mapping to 'exercises' table in SQLite."""
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    muscle_group = db.Column(db.String(50), nullable=False, index=True)
    equipment = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(30), nullable=False)  # 'Beginner' | 'Intermediate' | 'Advanced'
    instructions = db.Column(db.Text, nullable=False)
    default_sets = db.Column(db.Integer, nullable=False, default=3)
    default_reps = db.Column(db.Integer, nullable=False, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Return dict representation of exercise."""
        return {
            'id': self.id,
            'name': self.name,
            'muscle_group': self.muscle_group,
            'equipment': self.equipment,
            'difficulty': self.difficulty,
            'instructions': self.instructions,
            'default_sets': self.default_sets,
            'default_reps': self.default_reps,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<Exercise id={self.id} name='{self.name}' muscle_group='{self.muscle_group}'>"


INITIAL_EXERCISES = [
    {
        "name": "Push-up",
        "muscle_group": "Chest",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "instructions": "Place hands shoulder-width apart, lower body until chest nearly touches floor, keep core tight, push back up.",
        "default_sets": 3,
        "default_reps": 12
    },
    {
        "name": "Bodyweight Squat",
        "muscle_group": "Legs",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "instructions": "Stand with feet shoulder-width apart. Sit back into hips, lowering thighs parallel to ground while keeping chest up.",
        "default_sets": 3,
        "default_reps": 15
    },
    {
        "name": "Plank",
        "muscle_group": "Core",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "instructions": "Maintain a push-up or forearm position, keeping body in a straight line from head to heels. Hold position steadily.",
        "default_sets": 3,
        "default_reps": 30
    },
    {
        "name": "Pull-up",
        "muscle_group": "Back",
        "equipment": "Pull-up Bar",
        "difficulty": "Intermediate",
        "instructions": "Grasp bar with palms facing away, pull chest up to the bar squeezing lats, lower down with control.",
        "default_sets": 3,
        "default_reps": 8
    },
    {
        "name": "Dumbbell Bicep Curl",
        "muscle_group": "Arms",
        "equipment": "Dumbbell",
        "difficulty": "Beginner",
        "instructions": "Stand erect holding dumbbells at sides. Curl weights toward shoulders contracting biceps, slowly lower down.",
        "default_sets": 3,
        "default_reps": 12
    },
    {
        "name": "Dumbbell Shoulder Press",
        "muscle_group": "Shoulders",
        "equipment": "Dumbbell",
        "difficulty": "Intermediate",
        "instructions": "Hold dumbbells at shoulder height with palms forward. Press overhead until arms are extended, lower under control.",
        "default_sets": 3,
        "default_reps": 10
    },
    {
        "name": "Walking Lunge",
        "muscle_group": "Legs",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "instructions": "Step forward with one leg, lowering hips until both knees are bent at 90-degree angles. Push off back foot to step forward.",
        "default_sets": 3,
        "default_reps": 12
    },
    {
        "name": "Dumbbell Bench Press",
        "muscle_group": "Chest",
        "equipment": "Dumbbell",
        "difficulty": "Intermediate",
        "instructions": "Lie flat on bench holding dumbbells above chest. Lower weights to chest level, press back up smoothly.",
        "default_sets": 3,
        "default_reps": 10
    }
]


def seed_initial_exercises():
    """Seed default exercises if the exercises table is empty."""
    if Exercise.query.first() is None:
        for data in INITIAL_EXERCISES:
            exercise = Exercise(**data)
            db.session.add(exercise)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
