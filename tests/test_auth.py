"""
Tests de integración para el servicio de autenticación.

Valida los flujos de registro, login, refresh (rotación) y logout.
Ejecutar con: pytest tests/test_auth.py -v

Nota: Los tests requieren que el stack de docker-compose esté corriendo.
Para ejecutar manualmente:
  docker compose up -d
  pytest tests/test_auth.py -v
"""
import requests
import os
import uuid
import pytest

# URL base del servicio de autenticación
# Usar localhost:8004 para ejecución desde host, http://auth-service:8004 para ejecución dentro de Docker
AUTH_URL = os.getenv('AUTH_URL', 'http://localhost:8004')
TIMEOUT = 5

# Usuario de prueba único (con UUID para evitar conflictos en ejecuciones múltiples)
TEST_EMAIL = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_FULLNAME = "Test User Automated"


def _post(endpoint: str, json_data=None, form_data=None):
    """
    Realiza un POST a un endpoint del servicio.
    
    Args:
        endpoint: ruta sin dominio (e.g., '/register')
        json_data: dict para enviar en Content-Type application/json
        form_data: dict para enviar en Content-Type application/x-www-form-urlencoded
    
    Returns:
        Response object de requests
    """
    url = AUTH_URL + endpoint
    headers = {}
    
    if json_data:
        headers['Content-Type'] = 'application/json'
        resp = requests.post(url, json=json_data, headers=headers, timeout=TIMEOUT)
    elif form_data:
        resp = requests.post(url, data=form_data, timeout=TIMEOUT)
    else:
        resp = requests.post(url, timeout=TIMEOUT)
    
    return resp


@pytest.fixture(scope="module")
def auth_tokens():
    """
    Fixture que proporciona tokens válidos para usar en los tests.
    Se ejecuta una sola vez al inicio del módulo.
    """
    # Registrar usuario de prueba
    register_payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": TEST_FULLNAME
    }
    resp_register = _post('/register', json_data=register_payload)
    assert resp_register.status_code in (201, 400), \
        f"Failed to register: {resp_register.status_code} - {resp_register.text}"
    
    # Login para obtener tokens iniciales
    login_payload = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    resp_login = _post('/login', form_data=login_payload)
    assert resp_login.status_code == 200, \
        f"Failed to login: {resp_login.status_code} - {resp_login.text}"
    
    tokens = resp_login.json()
    return {
        'access_token': tokens.get('access_token'),
        'refresh_token': tokens.get('refresh_token'),
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD
    }


class TestAuthFlow:
    """Suite de tests para el flujo de autenticación."""
    
    def test_01_register_new_user(self):
        """[TEST 1] Registrar un nuevo usuario debe devolver 201 o 400 si ya existe."""
        email = f"newuser_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": email,
            "password": "NewPassword123!",
            "full_name": "New Test User"
        }
        response = _post('/register', json_data=payload)
        
        # Se espera 201 (Created) o 400 si ya existe
        assert response.status_code in (201, 400), \
            f"❌ Register failed with {response.status_code}: {response.text}"
        print(f"✓ Test 1 passed: Register returned {response.status_code}")
    
    def test_02_login_success(self, auth_tokens):
        """[TEST 2] Login con credenciales válidas debe devolver access y refresh tokens."""
        payload = {
            "username": auth_tokens['email'],
            "password": auth_tokens['password']
        }
        response = _post('/login', form_data=payload)
        
        assert response.status_code == 200, \
            f"❌ Login failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert 'access_token' in data, "❌ access_token not in response"
        assert 'refresh_token' in data, "❌ refresh_token not in response"
        assert len(data['access_token']) > 0, "❌ access_token is empty"
        assert len(data['refresh_token']) > 0, "❌ refresh_token is empty"
        
        print("✓ Test 2 passed: Login successful, tokens obtained")
    
    def test_03_refresh_token_rotation(self, auth_tokens):
        """[TEST 3] Refresh debe rotar el token (nuevo refresh_token != viejo)."""
        old_refresh = auth_tokens['refresh_token']
        
        payload = {"refresh_token": old_refresh}
        response = _post('/refresh', json_data=payload)
        
        assert response.status_code == 200, \
            f"❌ Refresh failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert 'access_token' in data, "❌ access_token not in response"
        assert 'refresh_token' in data, "❌ refresh_token not in response"
        
        new_refresh = data['refresh_token']
        assert new_refresh != old_refresh, \
            f"❌ Refresh token was not rotated: old={old_refresh[:10]}... new={new_refresh[:10]}..."
        assert len(new_refresh) > 0, "❌ new refresh_token is empty"
        
        print("✓ Test 3 passed: Refresh token rotated successfully")
    
    def test_04_old_refresh_token_invalid(self, auth_tokens):
        """[TEST 4] Viejo refresh_token debe ser inválido después de rotar."""
        # Login nuevamente para obtener un token
        login_payload = {
            "username": auth_tokens['email'],
            "password": auth_tokens['password']
        }
        resp_login = _post('/login', form_data=login_payload)
        assert resp_login.status_code == 200, \
            f"❌ Login failed: {resp_login.status_code}"
        
        old_refresh = resp_login.json()['refresh_token']
        
        # Rotar una vez
        resp_rotate = _post('/refresh', json_data={"refresh_token": old_refresh})
        assert resp_rotate.status_code == 200, \
            f"❌ Refresh failed: {resp_rotate.status_code}"
        
        # Intentar usar el viejo refresh_token debe fallar con 401
        resp_invalid = _post('/refresh', json_data={"refresh_token": old_refresh})
        assert resp_invalid.status_code == 401, \
            f"❌ Old refresh token should be invalid (401), got {resp_invalid.status_code}"
        
        print("✓ Test 4 passed: Old refresh token correctly invalidated")
    
    def test_05_logout_revokes_token(self, auth_tokens):
        """[TEST 5] Logout debe revocar el refresh_token (no servir después)."""
        # Login para obtener un token fresco
        login_payload = {
            "username": auth_tokens['email'],
            "password": auth_tokens['password']
        }
        resp_login = _post('/login', form_data=login_payload)
        assert resp_login.status_code == 200, \
            f"❌ Login failed: {resp_login.status_code}"
        
        refresh = resp_login.json()['refresh_token']
        
        # Logout
        resp_logout = _post('/logout', json_data={"refresh_token": refresh})
        assert resp_logout.status_code == 200, \
            f"❌ Logout failed: {resp_logout.status_code} - {resp_logout.text}"
        
        # Intentar usar el token revocado debe fallar con 401
        resp_after_logout = _post('/refresh', json_data={"refresh_token": refresh})
        assert resp_after_logout.status_code == 401, \
            f"❌ Revoked token should be invalid (401), got {resp_after_logout.status_code}"
        
        print("✓ Test 5 passed: Token revoked successfully after logout")
    
    def test_06_login_with_invalid_credentials(self):
        """[TEST 6] Login con credenciales inválidas debe fallar."""
        payload = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = _post('/login', form_data=payload)
        
        # Debe fallar con 401 o 400
        assert response.status_code in (401, 400), \
            f"❌ Expected 401/400 for invalid credentials, got {response.status_code}"
        
        print("✓ Test 6 passed: Invalid credentials correctly rejected")


def test_health():
    """[TEST 0] Health check: verificar que el servicio está disponible."""
    response = requests.get(AUTH_URL + '/health', timeout=TIMEOUT)
    assert response.status_code == 200, \
        f"❌ Health check failed: {response.status_code} - {response.text}"
    print("✓ Test 0 passed: Auth service is healthy")
