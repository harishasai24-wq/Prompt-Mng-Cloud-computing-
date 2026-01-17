import pytest
import json
import sys
import os

# Add the parent directory to sys.path so we can import app and models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User, Prompt, PromptVersion

@pytest.fixture
def client():
    app = create_app(config_name='testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_full_workflow(client):
    # ═════════════════════════════════════════════════════════════════════════
    # STEP 1: AUTHENTICATION
    # ═════════════════════════════════════════════════════════════════════════
    # Register
    reg_resp = client.post('/api/auth/register', json={
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert reg_resp.status_code == 201
    
    # Login
    login_resp = client.post('/api/auth/login', json={
        'username': 'test_user',
        'password': 'password123'
    })
    assert login_resp.status_code == 200
    token = login_resp.json['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # ═════════════════════════════════════════════════════════════════════════
    # STEP 2: PROMPT CREATION (v1)
    # ═════════════════════════════════════════════════════════════════════════
    create_resp = client.post('/api/prompts', headers=headers, json={
        'title': 'Test Prompt',
        'task_type': 'generation',
        'domain': 'coding',
        'prompt_text': 'Write a function.' # Short/bad prompt intentionally
    })
    assert create_resp.status_code == 201
    prompt_id = create_resp.json['prompt']['id']
    version_1_id = create_resp.json['prompt']['current_version']['id']
    
    print(f"\n[OK] Created Prompt ID: {prompt_id} (Version 1 ID: {version_1_id})")

    # ═════════════════════════════════════════════════════════════════════════
    # STEP 3: ITERATION (Create v2)
    # ═════════════════════════════════════════════════════════════════════════
    # Update prompt text to trigger versioning
    update_resp = client.put(f'/api/prompts/{prompt_id}', headers=headers, json={
        'prompt_text': 'Write a Python function to calculate Fibonacci. Use recursion.',
        'change_notes': 'Made it specific'
    })
    assert update_resp.status_code == 200
    assert 'new_version' in update_resp.json
    version_2_id = update_resp.json['new_version']['id']
    
    print(f"[OK] Updated Prompt. Created Version 2 ID: {version_2_id}")

    # ═════════════════════════════════════════════════════════════════════════
    # STEP 4: AI EVALUATION (Rule-Based)
    # ═════════════════════════════════════════════════════════════════════════
    # Evaluate Version 2
    eval_resp = client.post(f'/api/evaluate/{version_2_id}', headers=headers)
    assert eval_resp.status_code == 200
    
    scores = eval_resp.json['evaluation']
    print(f"[OK] Evaluation Complete for v2:")
    print(f"     Clarity: {scores['clarity_score']}")
    print(f"     Relevance: {scores['relevance_score']}")
    print(f"     Final Score: {scores['final_score']}")
    
    # Assert specific rule-based logic worked (e.g. 'coding' domain relevance)
    assert scores['relevance_score'] > 50  # Should be high because we used coding terms

    # ═════════════════════════════════════════════════════════════════════════
    # STEP 5: VERIFY ADVANCED ANALYTICS (TextStat & TextBlob)
    # ═════════════════════════════════════════════════════════════════════════
    details = eval_resp.json['details']
    assert 'readability' in details
    assert 'sentiment' in details
    
    print("\n[OK] Advanced Analytics Verified:")
    print(f"     Readability (Grade): {details['readability']['grade_level']}")
    print(f"     Sentiment (Polarity): {details['sentiment']['polarity']}")
    print(f"     Subjectivity: {details['sentiment']['subjectivity']}")

