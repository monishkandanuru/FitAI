# FitAI — AI Powered Fitness & Nutrition Coach

**Live Deployment:** [https://fit-ai-olive-delta.vercel.app](https://fit-ai-olive-delta.vercel.app)  
**Repository:** [https://github.com/monishkandanuru/FitAI](https://github.com/monishkandanuru/FitAI)

FitAI is a modular Python & Flask web application featuring a dark glassmorphism UI, real-time MediaPipe Pose computer vision exercise tracking, browser speech-synthesis voice coaching, pose-based body proportion & posture assessment, rule-based workout and macro planning, Chart.js progress analytics, and personalized coaching recommendations.

## Implemented Modules (Stages 1–5 Complete)

1. **Authentication & Account Security (`/auth/register`, `/auth/login`, `/auth/settings`)**
   - Password hashing via Werkzeug, protected session routes (`@login_required`), and account settings with current-password verification.
2. **Dashboard & Personalized Recommendations (`/auth/dashboard`)**
   - Live biometric, caloric, and workout telemetry derived from saved database records.
   - **Stage 4 Personalized Coaching Engine (`utils/recommendations.py`)** synthesizing BMI, workout logs, camera form scores, macro adherence, and posture assessments.
3. **Adult BMI Calculator (`/auth/bmi`, `/auth/bmi/save`)**
   - Server-validated BMI calculation, healthy reference weight range estimation, and persistent history.
4. **Workout Routine Architect (`/auth/workout`)**
   - Goal, experience level, and target muscle group filtering backed by seeded SQLite/PostgreSQL exercises (`models/exercise.py`, `utils/workout_generator.py`).
5. **Stage 1 & 2 — Computer Vision Exercise Counter & Voice Coach (`/auth/workout/camera`)**
   - Real-time MediaPipe Pose tracking supporting 7 exercises: **Push-Ups, Squats, Lunges, Jumping Jacks, Sit-Ups, Bicep Curls, and Shoulder Press**.
   - Live joint angle HUD, 5-second countdown, real-time biomechanical form scoring (`0–100%`) and corrective badges, Web Speech API Voice Coach with mute toggle, MET calorie burn calculation, and session summary modal saving directly to `WorkoutLog`.
6. **Stage 3 — Pose-Based Body Assessment (`/auth/body_assessment`)**
   - Webcam MediaPipe Pose scanner and calibration form measuring Shoulder-to-Hip ratio, Torso-to-Leg ratio, Posture Alignment, and Bilateral Symmetry with clear visual estimation disclaimers.
7. **Diet & Macro Intelligence Planner (`/auth/diet`)**
   - Mifflin-St Jeor BMR, activity-adjusted TDEE, and goal-specific Protein/Carbs/Fats macro splits (`utils/nutrition_calculator.py`).
8. **Progress Analytics & Chart.js Trends (`/auth/progress`)**
   - Interactive Chart.js visualizations for Weight & BMI trends, Calories & Protein intake, and Workout Frequency & Duration, plus full historical tables (including camera `Form Score` badges).

## Local Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run on port 5001 (avoids macOS AirPlay Receiver on port 5000)
./venv/bin/python -c "from app import create_app; app=create_app(); app.run(debug=True, port=5001)"
```

Run automated verification tests:

```bash
./venv/bin/python -m unittest discover -s tests -v
```

## Vercel Deployment

The repository includes `vercel.json`, `build.py`, and serverless-safe configuration in `config.py` and `app.py`:
- **Live Production URL**: [https://fit-ai-olive-delta.vercel.app](https://fit-ai-olive-delta.vercel.app)
- **Live Health Endpoint**: [https://fit-ai-olive-delta.vercel.app/health](https://fit-ai-olive-delta.vercel.app/health)
- **Database**: Set `DATABASE_URL` (or `POSTGRES_URL`) in Vercel Environment Variables to connect a persistent PostgreSQL database (Neon, Supabase, or Vercel Postgres), and set `SECRET_KEY` to a strong random string. If no `DATABASE_URL` is provided, the app automatically falls back to `/tmp/fitai.db` so serverless invocations never fail on read-only filesystems.
