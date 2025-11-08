import requests
import os
import time

BASE = os.getenv('AUTH_URL', 'http://auth-service:8004')
TEST_USER = {"email": "testuser@example.com", "password": "testpass123", "full_name": "Test User"}


def safe_post(path, json=None, data=None):
    url = BASE + path
    return requests.post(url, json=json, data=data, timeout=5)


def test_register_login_refresh_logout():
    # Register (acepta 201 o 400 si ya existe)
    r = safe_post('/register', json=TEST_USER)
    assert r.status_code in (201, 400)

    # Login
    r = safe_post('/login', data={"username": TEST_USER['email'], "password": TEST_USER['password']})
    assert r.status_code == 200
    login_data = r.json()
    assert 'access_token' in login_data
    assert 'refresh_token' in login_data
    old_refresh = login_data['refresh_token']

    # Refresh (rotate)
    r = safe_post('/refresh', json={"refresh_token": old_refresh})
    assert r.status_code == 200
    ref_data = r.json()
    assert 'access_token' in ref_data
    assert 'refresh_token' in ref_data
    new_refresh = ref_data['refresh_token']
    assert new_refresh != old_refresh

    # Old refresh must be invalid
    r = safe_post('/refresh', json={"refresh_token": old_refresh})
    assert r.status_code == 401

    # Logout with new refresh
    r = safe_post('/logout', json={"refresh_token": new_refresh})
    assert r.status_code == 200

    # New refresh must be invalid after logout
    r = safe_post('/refresh', json={"refresh_token": new_refresh})
    assert r.status_code == 401
