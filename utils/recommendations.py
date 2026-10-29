"""
Personalized AI & Rule-Based Coaching Recommendations Engine (Stage 4)
Synthesizes User Profile, BMI history, Workout frequency & rep volume,
Camera Form Compliance scores, Nutrition/Macro logs, and Body Assessment metrics
into actionable, personalized coaching recommendations.
"""

from typing import Dict, Any, List


def generate_personalized_recommendations(
    latest_bmi: Any = None,
    workout_logs: List[Any] = None,
    nutrition_logs: List[Any] = None,
    latest_assessment: Any = None,
    target_calories: int = 2200,
    target_protein_g: float = 140.0
) -> Dict[str, Any]:
    """
    Combines multi-module user telemetry to produce structured coaching recommendations,
    next suggested workout parameters, nutrition adjustments, and form cues.
    """
    workout_logs = workout_logs or []
    nutrition_logs = nutrition_logs or []

    recommendations: List[Dict[str, str]] = []
    readiness_score = 80
    recommended_goal = "General Fitness"
    recommended_focus = "Full Body"

    # 1. Analyze BMI & Biometric Status
    if latest_bmi:
        bmi_val = float(latest_bmi.bmi_value)
        height_m = float(latest_bmi.height_cm) / 100.0
        ideal_min_kg = round(18.5 * (height_m ** 2), 1)
        ideal_max_kg = round(24.9 * (height_m ** 2), 1)

        if bmi_val < 18.5:
            recommended_goal = "Muscle Gain"
            recommendations.append({
                "category": "Biometrics & Mass",
                "badge": "Caloric Surplus",
                "color": "#06b6d4",
                "title": "Prioritize Progressive Hypertrophy & Caloric Surplus",
                "detail": (
                    f"Your latest BMI is {bmi_val} ({latest_bmi.bmi_category}). "
                    f"Your healthy reference weight window is {ideal_min_kg}–{ideal_max_kg} kg. "
                    "Focus on compound resistance training 3–4x/week with a +350 kcal daily surplus."
                ),
                "action_url": "/auth/diet",
                "action_label": "Adjust Macro Surplus"
            })
        elif bmi_val < 25.0:
            recommended_goal = "Muscle Gain"
            recommendations.append({
                "category": "Biometrics & Mass",
                "badge": "Optimal BMI",
                "color": "#10b981",
                "title": "Maintain Lean Composition & Strength Progression",
                "detail": (
                    f"Your BMI of {bmi_val} is within the optimal adult reference range "
                    f"({ideal_min_kg}–{ideal_max_kg} kg). Focus on progressive overload and hitting daily protein targets."
                ),
                "action_url": "/auth/workout",
                "action_label": "Generate Strength Plan"
            })
        elif bmi_val < 30.0:
            recommended_goal = "Weight Loss"
            recommendations.append({
                "category": "Biometrics & Metabolic",
                "badge": "Recomposition",
                "color": "#f59e0b",
                "title": "Combine High-Protein Deficit with Metabolic Conditioning",
                "detail": (
                    f"Your latest BMI is {bmi_val} ({latest_bmi.bmi_category}, reference range {ideal_min_kg}–{ideal_max_kg} kg). "
                    "A moderate 250–500 kcal deficit paired with high protein preserves lean muscle while reducing fat mass."
                ),
                "action_url": "/auth/diet",
                "action_label": "Configure Deficit Macros"
            })
        else:
            recommended_goal = "Weight Loss"
            recommendations.append({
                "category": "Biometrics & Joint Care",
                "badge": "Low-Impact Burn",
                "color": "#f43f5e",
                "title": "Prioritize Consistent Low-Impact Volume & Steady Deficit",
                "detail": (
                    f"With a recorded BMI of {bmi_val}, prioritize joint-friendly movements (Squats, Bicep Curls, Shoulder Press) "
                    "and consistent daily caloric tracking."
                ),
                "action_url": "/auth/workout",
                "action_label": "Open Workout Planner"
            })
    else:
        recommendations.append({
            "category": "Baseline Setup",
            "badge": "Step 1",
            "color": "#10b981",
            "title": "Complete Your Baseline BMI & Biometric Profile",
            "detail": "Log your height, weight, and age in the BMI Calculator to unlock calibrated calorie and weight targets.",
            "action_url": "/auth/bmi",
            "action_label": "Calculate BMI"
        })

    # 2. Analyze Workout Performance & Camera Form Compliance
    scored_logs = [w for w in workout_logs if getattr(w, 'form_score', None) is not None]
    avg_form_score = (
        round(sum(w.form_score for w in scored_logs) / len(scored_logs))
        if scored_logs else None
    )

    if len(workout_logs) == 0:
        readiness_score -= 10
        recommendations.append({
            "category": "Training Consistency",
            "badge": "Start First Session",
            "color": "#06b6d4",
            "title": "Launch Your First AI Camera or Guided Workout",
            "detail": "You haven't logged a workout session yet. Try a 5-minute camera-tracked Push-Up or Squat session to benchmark your form.",
            "action_url": "/auth/workout/camera",
            "action_label": "Launch Camera Coach"
        })
    else:
        total_Duration = sum(w.duration_mins for w in workout_logs[:7])
        if avg_form_score is not None:
            if avg_form_score >= 85:
                readiness_score += 8
                recommendations.append({
                    "category": "Form & Biomechanics",
                    "badge": f"{avg_form_score}% Form Score",
                    "color": "#10b981",
                    "title": "Excellent Biomechanical Form — Ready to Increase Volume",
                    "detail": (
                        f"Your average camera form score across {len(scored_logs)} tracked session(s) is {avg_form_score}%. "
                        "Your joint alignment is solid—consider stepping up reps by 10–15% on your next set."
                    ),
                    "action_url": "/auth/workout/camera",
                    "action_label": "Start Next Tracked Set"
                })
            elif avg_form_score >= 70:
                recommendations.append({
                    "category": "Form & Biomechanics",
                    "badge": f"{avg_form_score}% Form Score",
                    "color": "#f59e0b",
                    "title": "Focus on Tempo & Full Range of Motion",
                    "detail": (
                        f"Your camera form score averages {avg_form_score}%. Slow down the eccentric (lowering) phase "
                        "and listen to the Voice Coach cues before adding extra speed."
                    ),
                    "action_url": "/auth/workout/camera",
                    "action_label": "Practice with Voice Coach"
                })
            else:
                readiness_score -= 5
                recommendations.append({
                    "category": "Form & Injury Prevention",
                    "badge": f"{avg_form_score}% Form Score",
                    "color": "#ef4444",
                    "title": "Prioritize Joint Alignment Over Rep Speed",
                    "detail": (
                        f"Your recent average form score is {avg_form_score}%. Reduce set size and focus on full extension "
                        "and spine alignment in the Camera Coach."
                    ),
                    "action_url": "/auth/workout/camera",
                    "action_label": "Recalibrate Form"
                })
        else:
            recommendations.append({
                "category": "Training Volume",
                "badge": f"{total_Duration} mins logged",
                "color": "#10b981",
                "title": "Add Live Camera Form Scoring to Your Routine",
                "detail": (
                    f"You've logged {len(workout_logs)} workout session(s) ({total_Duration} mins in recent logs). "
                    "Use the MediaPipe Workout Camera on your next set to track joint angles and form accuracy."
                ),
                "action_url": "/auth/workout/camera",
                "action_label": "Try Camera Counter"
            })

    # 3. Analyze Nutrition & Protein Compliance
    if nutrition_logs:
        latest_nut = nutrition_logs[0]
        cal_diff = latest_nut.calories_consumed - target_calories
        prot_gap = round(target_protein_g - float(latest_nut.protein_grams), 1)

        if prot_gap > 25:
            recommendations.append({
                "category": "Nutrition & Recovery",
                "badge": f"+{prot_gap}g Protein Needed",
                "color": "#f59e0b",
                "title": "Boost Daily Protein Intake for Muscle Recovery",
                "detail": (
                    f"Your latest nutrition log recorded {latest_nut.protein_grams}g protein against a target of "
                    f"{target_protein_g}g ({latest_nut.calories_consumed} kcal logged). Add a lean protein source post-workout."
                ),
                "action_url": "/auth/progress",
                "action_label": "Log Today's Nutrition"
            })
        else:
            readiness_score += 5
            recommendations.append({
                "category": "Nutrition & Recovery",
                "badge": "Macro Aligned",
                "color": "#06b6d4",
                "title": "Strong Protein & Caloric Consistency",
                "detail": (
                    f"Your latest entry ({latest_nut.calories_consumed} kcal, {latest_nut.protein_grams}g protein) "
                    f"is well aligned with your {target_calories} kcal daily target."
                ),
                "action_url": "/auth/progress",
                "action_label": "View Nutrition Trends"
            })
    else:
        recommendations.append({
            "category": "Nutrition Tracking",
            "badge": "Unlogged",
            "color": "#06b6d4",
            "title": "Log Your First Daily Meal & Macro Entry",
            "detail": f"Your estimated daily target is {target_calories} kcal with {target_protein_g}g protein. Log your daily intake in Progress to track adherence.",
            "action_url": "/auth/progress",
            "action_label": "Log Nutrition"
        })

    # 4. Analyze Body Assessment & Posture (Stage 3 integration)
    if latest_assessment:
        if latest_assessment.posture_score < 80 or latest_assessment.symmetry_score < 80:
            recommended_focus = "Core"
            recommendations.append({
                "category": "Posture & Proportions",
                "badge": f"Posture {latest_assessment.posture_score}%",
                "color": "#8b5cf6",
                "title": "Add Core & Shoulder Stability Work",
                "detail": (
                    f"Your latest Body Assessment ({latest_assessment.frame_category}, posture {latest_assessment.posture_score}%, "
                    f"symmetry {latest_assessment.symmetry_score}%) suggests focusing on unilateral and core stability exercises."
                ),
                "action_url": "/auth/body_assessment",
                "action_label": "Review Body Assessment"
            })
        else:
            readiness_score += 5
            recommendations.append({
                "category": "Posture & Proportions",
                "badge": f"Posture {latest_assessment.posture_score}%",
                "color": "#8b5cf6",
                "title": f"Balanced Alignment ({latest_assessment.frame_category})",
                "detail": (
                    f"Pose assessment shows {latest_assessment.posture_score}% posture alignment and "
                    f"a {latest_assessment.shoulder_hip_ratio:.2f} shoulder-to-hip ratio."
                ),
                "action_url": "/auth/body_assessment",
                "action_label": "Open Body Scanner"
            })
    else:
        recommendations.append({
            "category": "Body Assessment",
            "badge": "New Module",
            "color": "#8b5cf6",
            "title": "Run a Pose-Based Body Proportion & Posture Scan",
            "detail": "Use your webcam with MediaPipe Pose to estimate shoulder-to-hip proportions, torso-to-leg ratio, and posture symmetry.",
            "action_url": "/auth/body_assessment",
            "action_label": "Run Body Scan"
        })

    readiness_score = max(50, min(99, readiness_score))

    return {
        "readiness_score": readiness_score,
        "recommended_goal": recommended_goal,
        "recommended_focus": recommended_focus,
        "avg_form_score": avg_form_score,
        "items": recommendations
    }
