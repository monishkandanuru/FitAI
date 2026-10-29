"""
Workout Generator Logic
Provides rule-based exercise selection and custom routine generation from the SQLite database
based on the user's selected goal, experience level, and target muscle group focus.
"""

from typing import Dict, Any, List
from models import Exercise


GOAL_PRESETS = {
    "Muscle Gain": {"sets": 4, "reps": "8 – 12 reps", "tempo": "Moderate / Control"},
    "Weight Loss": {"sets": 3, "reps": "12 – 15 reps", "tempo": "Fast / High Energy"},
    "Endurance":   {"sets": 3, "reps": "15 – 20 reps", "tempo": "Steady Pace"},
    "General Fitness": {"sets": 3, "reps": "10 – 12 reps", "tempo": "Controlled Tempo"}
}


def generate_workout_plan(goal: str = "Muscle Gain", fitness_level: str = "Beginner", focus: str = "Full Body") -> Dict[str, Any]:
    """
    Selects exercises from the Exercise model database matching goal, fitness level, and target focus area.
    Returns a structured workout plan dictionary.
    """
    goal = goal.strip() if goal else "Muscle Gain"
    fitness_level = fitness_level.strip().capitalize() if fitness_level else "Beginner"
    focus = focus.strip() if focus else "Full Body"

    # Default goal config fallback
    preset = GOAL_PRESETS.get(goal, GOAL_PRESETS["General Fitness"])
    
    # Adjust sets for beginner
    if fitness_level == "Beginner" and preset["sets"] > 3:
        sets_count = 3
    else:
        sets_count = preset["sets"]

    # Query exercises from SQLite
    query = Exercise.query

    # Filter by difficulty according to user level
    if fitness_level == "Beginner":
        query = query.filter(Exercise.difficulty.in_(["Beginner"]))
    elif fitness_level == "Intermediate":
        query = query.filter(Exercise.difficulty.in_(["Beginner", "Intermediate"]))
    
    # Filter by muscle group focus if not Full Body
    if focus != "Full Body":
        query = query.filter(Exercise.muscle_group.ilike(f"%{focus}%"))

    exercises_found = query.all()

    # Fallback to all exercises if query results are limited
    if len(exercises_found) < 3:
        exercises_found = Exercise.query.all()

    planned_exercises: List[Dict[str, Any]] = []
    for ex in exercises_found:
        reps_str = "30 – 45 seconds" if ex.name.lower() == "plank" else preset["reps"]
        
        planned_exercises.append({
            "id": ex.id,
            "name": ex.name,
            "muscle_group": ex.muscle_group,
            "equipment": ex.equipment,
            "difficulty": ex.difficulty,
            "instructions": ex.instructions,
            "sets": sets_count,
            "reps": reps_str
        })

    total_exercises = len(planned_exercises)
    est_duration = max(15, total_exercises * 6)

    return {
        "title": f"{fitness_level} {goal} Routine",
        "goal": goal,
        "fitness_level": fitness_level,
        "focus": focus,
        "total_exercises": total_exercises,
        "estimated_duration_mins": est_duration,
        "exercises": planned_exercises
    }
