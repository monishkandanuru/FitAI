import re
from unittest.mock import patch
import pytest
from app import create_app
from models import db, User, BmiRecord, Activity

@pytest.fixture
def app():
    app = create_app('testing')
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def token(client, page='/auth/login'):
    body = client.get(page).text
    return re.search(r'name="csrf_token" value="([^"]+)"', body)[1]

def register(client, email='one@example.com'):
    return client.post('/auth/register', data=dict(csrf_token=token(client, '/auth/register'), full_name='Test Person', email=email, password='Test-password-123', confirm_password='Test-password-123'), follow_redirects=True)

def save(client, **overrides):
    data = dict(height_cm=175, weight_kg=70, age=25, gender='male', bmi_value=999, bmi_category='forged')
    data.update(overrides)
    return client.post('/auth/bmi/save', json=data, headers={'X-CSRFToken':token(client, '/auth/bmi')})

def test_public_routes_and_csrf(client):
    for path in ['/', '/health', '/auth/login', '/auth/register', '/static/css/style.css', '/static/js/script.js']:
        assert client.get(path).status_code == 200
    assert client.get('/missing').status_code == 404
    assert client.get('/auth/dashboard').status_code == 302
    assert client.post('/auth/register', data={}).status_code == 400
    assert client.get('/auth/logout').status_code == 405

def test_registration_all_pages_and_logout(client):
    assert register(client).status_code == 200
    for path in ['dashboard','profile','bmi','workout','diet','progress','settings']:
        response = client.get('/auth/' + path)
        assert response.status_code == 200, path
        assert 'Coming Soon' not in response.text
    response=client.post('/auth/logout', data={'csrf_token':token(client, '/auth/settings')})
    assert response.status_code == 302
    assert client.get('/auth/dashboard').status_code == 302

def test_bmi_recomputed_persisted_and_visible(client, app):
    register(client)
    assert save(client).status_code == 200
    with app.app_context():
        record = BmiRecord.query.one()
        assert record.bmi_value == 22.9
        assert record.bmi_category == 'Normal Weight'
    assert '22.9' in client.get('/auth/dashboard').text
    assert '70.0 kg' in client.get('/auth/progress').text

@pytest.mark.parametrize('data', [{'height_cm':'nan'}, {'height_cm':'inf'}, {'height_cm':0}, {'weight_kg':-5}, {'age':19}, {'age':25.5}, {'gender':'invalid'}, {'weight_kg':700}, {'age':float('inf')}])
def test_invalid_bmi_does_not_write(client, app, data):
    register(client)
    assert save(client, **data).status_code == 400
    with app.app_context():
        assert BmiRecord.query.count()==0

def test_bmi_json_shape(client):
    register(client)
    for payload in [[], [1], 'text', None]:
        assert client.post('/auth/bmi/save', json=payload, headers={'X-CSRFToken': token(client, '/auth/bmi')}).status_code==400

def test_user_isolation(client, app):
    register(client)
    save(client)
    other=app.test_client()
    register(other, 'two@example.com')
    assert '70.0 kg' not in other.get('/auth/progress').text
    assert 'Your story starts here.' in other.get('/auth/progress').text

def test_journals_update_dashboard(client, app):
    register(client)
    for kind, amount in [('workout',35), ('diet',550)]:
        response=client.post('/auth/'+kind, data={'csrf_token':token(client,'/auth/'+kind), 'label':'Test entry', 'amount':amount, 'day':'2026-01-01'}, follow_redirects=True)
        assert response.status_code==200
        assert 'Test entry' in response.text
    with app.app_context():
        assert Activity.query.count()==2
    response=client.post('/auth/workout',data={'csrf_token':token(client,'/auth/workout'),'label':'bad','amount':-1,'day':'2026-01-01'})
    assert 'valid amount' in response.text

def test_settings_password(client, app):
    register(client)
    response=client.post('/auth/settings',data={'csrf_token':token(client,'/auth/settings'),'full_name':'New Name','current_password':'Test-password-123','new_password':'Changed-password-123','confirm_password':'Changed-password-123'},follow_redirects=True)
    assert response.status_code==200
    with app.app_context():
        user=User.query.one()
        assert user.full_name=='New Name'
        assert user.check_password('Changed-password-123')
        assert not user.check_password('Test-password-123')

@pytest.mark.parametrize('target',['//evil.example','/\\evil.example','https://evil.example','/\tevil.example'])
def test_no_open_redirect(client, target):
    register(client)
    client.post('/auth/logout',data={'csrf_token':token(client,'/auth/settings')})
    response=client.post('/auth/login',query_string={'next':target},data={'csrf_token':token(client),'email':'one@example.com','password':'Test-password-123'})
    assert response.location=='/auth/dashboard'

def test_health_detects_database_failure(client):
    with patch('routes.main.db.session.execute',side_effect=RuntimeError('secret database URL')):
        response=client.get('/health')
        assert response.status_code==503
        assert 'secret' not in response.text

def test_security_headers(client):
    response=client.get('/auth/login')
    assert response.headers['X-Frame-Options']=='DENY'
    assert response.headers['Cache-Control']=='no-store'

def test_production_requires_secret(monkeypatch):
    monkeypatch.delenv('SECRET_KEY',raising=False)
    with pytest.raises(RuntimeError,match='SECRET_KEY'):
        create_app('production')

def test_calculator_form_result(client):
    register(client)
    response=client.post('/auth/bmi',data={'csrf_token':token(client,'/auth/bmi'),'height_cm':175,'weight_kg':70,'age':30,'gender':'female'})
    assert response.status_code==200
    assert '22.9' in response.text
    assert 'X-CSRFToken' in response.text
    assert 'save-result-btn' in response.text

def test_no_bmi_write_without_csrf(client, app):
    register(client)
    assert client.post('/auth/bmi/save',json={'height_cm':175}).status_code==400
    with app.app_context():
        assert BmiRecord.query.count()==0

def test_actual_daily_totals(client):
    from datetime import datetime, timezone
    register(client)
    today=datetime.now(timezone.utc).date().isoformat()
    for kind,amount in [('workout',37),('diet',543)]:
        client.post('/auth/'+kind,data={'csrf_token':token(client,'/auth/'+kind),'label':'Today entry','amount':amount,'day':today})
    html=client.get('/auth/dashboard').text
    assert '<strong>37 ' in html
    assert '<strong>543 ' in html

def test_duplicate_account_rejected(client, app):
    register(client)
    other=app.test_client()
    assert 'already exists' in register(other).text
    with app.app_context():
        assert User.query.count()==1

def test_settings_reject_wrong_password(client, app):
    register(client)
    response=client.post('/auth/settings',data={'csrf_token':token(client,'/auth/settings'),'full_name':'Changed','current_password':'wrong'})
    assert 'incorrect' in response.text
    with app.app_context():
        assert User.query.one().full_name=='Test Person'
