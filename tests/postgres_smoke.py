"""Run only against the disposable PostgreSQL database in CI."""
import re
from app import app
from models import db, BmiRecord
with app.app_context():
    db.create_all()
client = app.test_client()
def token(path):
    return re.search(r'name="csrf_token" value="([^"]+)"', client.get(path, base_url='https://localhost').text)[1]
response = client.post('/auth/register', base_url='https://localhost', headers={'Referer':'https://localhost/auth/register'}, data={
    'csrf_token':token('/auth/register'), 'full_name':'CI Test', 'email':'ci@example.com',
    'password':'ci-only-password', 'confirm_password':'ci-only-password'})
assert response.status_code == 302
response = client.post('/auth/bmi/save', base_url='https://localhost', headers={
    'X-CSRFToken':token('/auth/bmi'), 'Referer':'https://localhost/auth/bmi'},
    json={'height_cm':175, 'weight_kg':70, 'age':30, 'gender':'male'})
assert response.status_code == 200, response.text
with app.app_context():
    assert BmiRecord.query.one().bmi_value == 22.9
assert client.get('/health', base_url='https://localhost').status_code == 200
assert '70.0 kg' in client.get('/auth/progress', base_url='https://localhost').text
print('Production-mode PostgreSQL registration, BMI persistence, history and health passed.')
