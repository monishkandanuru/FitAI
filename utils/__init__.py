"""
FitAI Utilities Package
Exposes workout generation, nutrition calculation, and personalized recommendation engines.
"""

from utils.workout_generator import generate_workout_plan
from utils.nutrition_calculator import calculate_bmr, calculate_tdee, calculate_nutrition_targets
from utils.recommendations import generate_personalized_recommendations

__all__ = [
    'generate_workout_plan',
    'calculate_bmr',
    'calculate_tdee',
    'calculate_nutrition_targets',
    'generate_personalized_recommendations'
]
