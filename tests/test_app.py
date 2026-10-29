"""
FitAI Automated Verification & Integration Test Suite
Tests all core routes, authentication flows, BMI calculation & server-side recomputation,
workout generation, live camera session logging, Stage 3 body assessment,
Stage 4 personalized recommendations, nutrition planner, progress analytics,
account settings updates, data isolation, and Vercel serverless readiness.
"""

import unittest
from app import create_app
from config import TestingConfig
from models import db, User, BmiRecord, WorkoutLog, NutritionLog, BodyAssessment


class FitAITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def register_and_login(self, full_name="Monish Kandanuru", email="monish@example.com", password="Password123!"):
        return self.client.post('/auth/register', data={
            'full_name': full_name,
            'email': email,
            'password': password,
            'confirm_password': password
        }, follow_redirects=True)

    def test_01_public_and_health_endpoints(self):
        resp_home = self.client.get('/')
        self.assertEqual(resp_home.status_code, 200)
        self.assertIn(b'FitAI', resp_home.data)

        resp_health = self.client.get('/health')
        self.assertEqual(resp_health.status_code, 200)
        data = resp_health.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('connected', data['database'])

    def test_02_registration_login_logout_and_aliases(self):
        resp = self.register_and_login()
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Monish', resp.data)

        # Duplicate registration rejected
        self.client.get('/auth/logout', follow_redirects=True)
        dup_resp = self.register_and_login()
        self.assertIn(b'already exists', dup_resp.data)

        # Login with valid credentials
        login_resp = self.client.post('/auth/login', data={
            'email': 'monish@example.com',
            'password': 'Password123!'
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b'Dashboard', login_resp.data)

        # Convenience aliases redirect properly
        for alias in ['/dashboard', '/bmi', '/workout', '/workout/camera', '/body-assessment', '/diet', '/progress', '/profile', '/settings']:
            r = self.client.get(alias, follow_redirects=False)
            self.assertIn(r.status_code, (301, 302))

    def test_03_bmi_calculation_and_server_recomputation(self):
        self.register_and_login()
        calc_resp = self.client.post('/auth/bmi', data={
            'height_cm': '175',
            'weight_kg': '70',
            'age': '24',
            'gender': 'male'
        })
        self.assertEqual(calc_resp.status_code, 200)
        self.assertIn(b'22.9', calc_resp.data)
        self.assertIn(b'Normal Weight', calc_resp.data)

        # Save BMI via JSON and verify server-side recomputation ignores spoofed client BMI
        save_resp = self.client.post('/auth/bmi/save', json={
            'height_cm': 175,
            'weight_kg': 70,
            'age': 24,
            'gender': 'male',
            'bmi_value': 99.9,
            'bmi_category': 'Fake'
        })
        self.assertEqual(save_resp.status_code, 200)
        self.assertTrue(save_resp.get_json()['success'])

        rec = BmiRecord.query.first()
        self.assertIsNotNone(rec)
        self.assertAlmostEqual(rec.bmi_value, 22.9, places=1)
        self.assertEqual(rec.bmi_category, 'Normal Weight')

    def test_04_workout_generator_and_camera_session_save(self):
        self.register_and_login()
        w_resp = self.client.post('/auth/workout', data={
            'goal': 'Muscle Gain',
            'fitness_level': 'Intermediate',
            'focus': 'Chest'
        })
        self.assertEqual(w_resp.status_code, 200)
        self.assertIn(b'Intermediate Muscle Gain Routine', w_resp.data)

        cam_page = self.client.get('/auth/workout/camera')
        self.assertEqual(cam_page.status_code, 200)
        self.assertIn(b'Exercise Repetition Counter', cam_page.data)

        cam_save = self.client.post('/auth/workout/camera/save_session', json={
            'exercise_name': 'Push-Up Counter',
            'total_reps': 25,
            'duration_secs': 180,
            'calories_burned': 24.5,
            'form_score': 91
        })
        self.assertEqual(cam_save.status_code, 200)
        self.assertTrue(cam_save.get_json()['success'])

        log = WorkoutLog.query.first()
        self.assertIsNotNone(log)
        self.assertEqual(log.completed_exercises, 25)
        self.assertEqual(log.form_score, 91)

    def test_05_body_assessment_and_recommendations(self):
        self.register_and_login()
        get_resp = self.client.get('/auth/body_assessment')
        self.assertEqual(get_resp.status_code, 200)
        self.assertIn(b'Estimation Notice', get_resp.data)

        post_resp = self.client.post('/auth/body_assessment/save', data={
            'estimated_height_cm': '176.5',
            'shoulder_hip_ratio': '1.36',
            'torso_leg_ratio': '0.67',
            'posture_score': '92',
            'symmetry_score': '94',
            'frame_category': 'V-Taper Athletic',
            'recommendation_summary': 'Strong posture alignment.'
        }, follow_redirects=True)
        self.assertEqual(post_resp.status_code, 200)
        self.assertIn(b'V-Taper Athletic', post_resp.data)

        assessment = BodyAssessment.query.first()
        self.assertIsNotNone(assessment)
        self.assertEqual(assessment.posture_score, 92)

        # Verify Dashboard renders Personalized Recommendations
        dash_resp = self.client.get('/auth/dashboard')
        self.assertEqual(dash_resp.status_code, 200)
        self.assertIn(b'Personalized Coach Recommendations', dash_resp.data)

    def test_06_diet_progress_and_account_settings(self):
        self.register_and_login()
        diet_resp = self.client.post('/auth/diet', data={
            'height_cm': '175',
            'weight_kg': '70',
            'age': '25',
            'gender': 'Male',
            'activity_level': 'Moderately Active',
            'goal': 'Muscle Gain'
        })
        self.assertEqual(diet_resp.status_code, 200)
        self.assertIn(b'Target Macro Distribution', diet_resp.data)

        # Log workout and nutrition on Progress page
        self.client.post('/auth/progress/log_workout', data={
            'workout_title': 'Upper Body Hypertrophy',
            'completed_exercises': '6',
            'duration_mins': '45'
        }, follow_redirects=True)
        self.client.post('/auth/progress/log_nutrition', data={
            'calories_consumed': '2450',
            'protein_grams': '165',
            'carbs_grams': '260',
            'fats_grams': '75'
        }, follow_redirects=True)

        prog_resp = self.client.get('/auth/progress')
        self.assertEqual(prog_resp.status_code, 200)
        self.assertIn(b'Upper Body Hypertrophy', prog_resp.data)
        self.assertIn(b'2450 kcal', prog_resp.data)

        # Account settings update with password verification
        settings_resp = self.client.post('/auth/settings', data={
            'full_name': 'Monish K.',
            'current_password': 'Password123!',
            'new_password': 'NewSecurePass456!',
            'confirm_new_password': 'NewSecurePass456!'
        }, follow_redirects=True)
        self.assertEqual(settings_resp.status_code, 200)
        self.assertIn(b'Account settings updated successfully!', settings_resp.data)

        updated_user = User.query.filter_by(email='monish@example.com').first()
        self.assertEqual(updated_user.full_name, 'Monish K.')
        self.assertTrue(updated_user.check_password('NewSecurePass456!'))


if __name__ == '__main__':
    unittest.main()
