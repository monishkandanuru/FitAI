"""
Nutrition & Macro Intelligence Calculator
Calculates BMR (Mifflin-St Jeor), TDEE, Caloric Targets, and Macro Splits (Protein, Carbs, Fats).
"""

from typing import Dict, Any


ACTIVITY_MULTIPLIERS = {
    "Sedentary": 1.2,
    "Lightly Active": 1.375,
    "Moderately Active": 1.55,
    "Very Active": 1.725,
    "Extra Active": 1.9
}


GOAL_CALORIE_ADJUSTMENTS = {
    "Weight Loss": -500,
    "Mild Weight Loss": -250,
    "Maintenance": 0,
    "Muscle Gain": 350,
    "Extreme Gain": 500
}


MACRO_SPLITS = {
    "Weight Loss": {"protein": 0.35, "carbs": 0.35, "fats": 0.30},
    "Mild Weight Loss": {"protein": 0.30, "carbs": 0.40, "fats": 0.30},
    "Maintenance": {"protein": 0.25, "carbs": 0.50, "fats": 0.25},
    "Muscle Gain": {"protein": 0.30, "carbs": 0.50, "fats": 0.20},
    "Extreme Gain": {"protein": 0.30, "carbs": 0.55, "fats": 0.15}
}


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Calculates Basal Metabolic Rate using the Mifflin-St Jeor equation.
    """
    gender_clean = str(gender).lower().strip()
    base = (10.0 * float(weight_kg)) + (6.25 * float(height_cm)) - (5.0 * int(age))
    if gender_clean == 'female':
        return round(base - 161.0, 1)
    else:
        return round(base + 5.0, 1)


def calculate_tdee(bmr: float, activity_level: str = "Moderately Active") -> float:
    """
    Calculates Total Daily Energy Expenditure from BMR and activity multiplier.
    """
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 1)


def calculate_nutrition_targets(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str = "Moderately Active",
    goal: str = "Maintenance"
) -> Dict[str, Any]:
    """
    Returns complete macro intelligence payload containing BMR, TDEE, daily target calories,
    and protein, carb, fat distributions.
    """
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)

    adj = GOAL_CALORIE_ADJUSTMENTS.get(goal, 0)
    target_calories = max(1200, int(round(tdee + adj)))

    split = MACRO_SPLITS.get(goal, MACRO_SPLITS["Maintenance"])

    protein_cal = target_calories * split["protein"]
    carbs_cal = target_calories * split["carbs"]
    fats_cal = target_calories * split["fats"]

    protein_grams = round(protein_cal / 4.0, 1)
    carbs_grams = round(carbs_cal / 4.0, 1)
    fats_grams = round(fats_cal / 9.0, 1)

    return {
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "age": age,
        "gender": gender.capitalize() if isinstance(gender, str) else 'Male',
        "activity_level": activity_level,
        "goal": goal,
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_calories,
        "macros": {
            "protein": {
                "grams": protein_grams,
                "calories": int(round(protein_cal)),
                "percentage": int(round(split["protein"] * 100))
            },
            "carbs": {
                "grams": carbs_grams,
                "calories": int(round(carbs_cal)),
                "percentage": int(round(split["carbs"] * 100))
            },
            "fats": {
                "grams": fats_grams,
                "calories": int(round(fats_cal)),
                "percentage": int(round(split["fats"] * 100))
            }
        }
    }
