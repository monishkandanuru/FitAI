"""Shared validation for calculated and saved adult BMI measurements."""
import math

def calculate(data):
    try:
        height = float(data.get('height_cm', 0))
        weight = float(data.get('weight_kg', 0))
        age_number = float(data.get('age', 0))
        if not all(math.isfinite(v) for v in (height, weight, age_number)):
            raise ValueError
        if not 50 <= height <= 300 or not 1 <= weight <= 600:
            raise ValueError('Enter height from 50–300 cm and weight from 1–600 kg.')
        if not age_number.is_integer() or not 20 <= age_number <= 120:
            raise ValueError('This adult BMI calculator supports ages 20–120.')
        gender = str(data.get('gender', '')).lower()
        if gender not in ('male', 'female'):
            raise ValueError('Please select a valid gender.')
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(str(exc) or 'Enter valid, finite measurements.') from None
    raw = weight / (height / 100) ** 2
    category, css = ('Underweight', 'underweight') if raw < 18.5 else (('Normal Weight', 'normal') if raw < 25 else (('Overweight', 'overweight') if raw < 30 else ('Obese', 'obese')))
    return dict(height_cm=height, weight_kg=weight, age=int(age_number), gender=gender,
                bmi_value=round(raw, 1), bmi_category=category, category_class='bmi-' + css)
