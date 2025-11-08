import pytest
from fastapi.testclient import TestClient
from services.authentication.main import app

client = TestClient(app)

TEST_USER = {"email": "testuser@example.com", "password": "testpass123", "full_name": "Test User"}

@pytest.fixture(autouse=True)
def cleanup_db():
    # Intenta limpiar colecciones si están disponibles (esto asume que el servicio usa motor AsyncIOMotorClient)
    try:
        import asyncio
        from services.authentication import main as auth_main
        loop = asyncio.get_event_loop()
        async def clear():
            await auth_main.users_col.delete_many({"email": TEST_USER['email']})
            await auth_main.refresh_col.delete_many({"email": TEST_USER['email']})
        loop.run_until_complete(clear())
    except Exception:
        pass
    yield
    try:
        import asyncio
        from services.authentication import main as auth_main
        loop = asyncio.get_event_loop()
        async def clear():
            await auth_main.users_col.delete_many({"email": TEST_USER['email']})
            await auth_main.refresh_col.delete_many({"email": TEST_USER['email']})
        loop.run_until_complete(clear())
    except Exception:
        pass

def test_register_login_refresh_logout():
    # Register
    r = client.post("/register", json=TEST_USER)
    assert r.status_code == 201
    data = r.json()
    assert data['email'] == TEST_USER['email']

    # Login
    r = client.post("/login", data={"username": TEST_USER['email'], "password": TEST_USER['password']})
    assert r.status_code == 200
    login_data = r.json()
    assert 'access_token' in login_data
    assert 'refresh_token' in login_data
    old_refresh = login_data['refresh_token']

    # Refresh (rotate)
    r = client.post("/refresh", json={"refresh_token": old_refresh})
    assert r.status_code == 200
    ref_data = r.json()
    assert 'access_token' in ref_data
    assert 'refresh_token' in ref_data
    new_refresh = ref_data['refresh_token']
    assert new_refresh != old_refresh

    # Old refresh must be invalid
    r = client.post("/refresh", json={"refresh_token": old_refresh})
    assert r.status_code == 401

    # Logout with new refresh
    r = client.post("/logout", json={"refresh_token": new_refresh})
    assert r.status_code == 200

    # New refresh must be invalid after logout
    r = client.post("/refresh", json={"refresh_token": new_refresh})
    assert r.status_code == 401
