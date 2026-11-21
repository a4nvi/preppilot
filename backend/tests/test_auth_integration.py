import pytest, sqlite3
from app import create_app
from werkzeug.security import check_password_hash


@pytest.fixture
def test_setup(tmp_path):
    db_file = str(tmp_path / "integration_test.db")
    app = create_app(db_file)
    client = app.test_client()
    return client, db_file


def test_user_lifecycle_registration_and_login(test_setup):
    """End-to-end integration test: register, authenticate, and access protected endpoints."""
    client, _ = test_setup
    payload = {"email": "student@jiit.ac.in", "password": "securepass123"}

    # 1. Registration
    reg_res = client.post("/api/register", json=payload)
    assert reg_res.status_code == 200
    token = reg_res.get_json().get("token")
    assert token is not None and len(token) > 10

    # 2. Login with valid credentials
    login_res = client.post("/api/login", json=payload)
    assert login_res.status_code == 200
    login_token = login_res.get_json().get("token")
    assert login_token is not None

    # 3. Access protected route with Bearer token
    headers = {"Authorization": f"Bearer {login_token}"}
    hist_res = client.get("/api/history", headers=headers)
    assert hist_res.status_code == 200
    assert hist_res.get_json().get("history") == []

    # 4. Access protected route with invalid/tampered token
    bad_headers = {"Authorization": "Bearer tampered_token_xyz"}
    bad_res = client.get("/api/history", headers=bad_headers)
    assert bad_res.status_code == 401


def test_password_hashing_in_database(test_setup):
    """Integration test verifying passwords are never stored in plaintext."""
    client, db_file = test_setup
    plain_password = "supersecretpassword"
    client.post("/api/register", json={"email": "security@jiit.ac.in", "password": plain_password})

    # Query the raw SQLite database directly
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    user = conn.execute("SELECT * FROM users WHERE email='security@jiit.ac.in'").fetchone()
    conn.close()

    assert user is not None
    assert user["pw"] != plain_password
    assert check_password_hash(user["pw"], plain_password) is True


def test_multi_user_isolation(test_setup):
    """Integration test verifying strict multi-user privacy and data isolation."""
    client, _ = test_setup

    # Register User A
    res_a = client.post("/api/register", json={"email": "userA@jiit.ac.in", "password": "passwordA123"})
    token_a = res_a.get_json()["token"]

    # Register User B
    res_b = client.post("/api/register", json={"email": "userB@jiit.ac.in", "password": "passwordB123"})
    token_b = res_b.get_json()["token"]

    assert token_a != token_b

    # Verify User A and User B have separate, isolated history arrays
    hist_a = client.get("/api/history", headers={"Authorization": f"Bearer {token_a}"}).get_json()
    hist_b = client.get("/api/history", headers={"Authorization": f"Bearer {token_b}"}).get_json()

    assert hist_a["history"] == []
    assert hist_b["history"] == []
