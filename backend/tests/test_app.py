import pytest
from app import create_app
import matcher, llm


@pytest.fixture
def client(tmp_path):
    return create_app(str(tmp_path / "t.db")).test_client()


def register(c):
    return c.post("/api/register", json={"email": "a@b.com", "password": "secret1"})


def test_matcher_score_and_gaps():
    r = matcher.compare("I know Python and SQL", "Need python, sql, docker")
    assert r["score"] == 67 and r["missing"] == ["docker"]


def test_register_then_login(client):
    assert register(client).status_code == 200
    assert client.post("/api/login", json={"email": "a@b.com", "password": "bad"}).status_code == 401
    assert client.post("/api/login", json={"email": "a@b.com", "password": "secret1"}).status_code == 200


def test_register_and_login_empty_fields(client):
    # Empty email
    r1 = client.post("/api/register", json={"email": "", "password": "secretpassword"})
    assert r1.status_code == 400
    assert "valid email" in r1.get_json()["error"].lower()

    # Empty password or password too short
    r2 = client.post("/api/register", json={"email": "test@example.com", "password": ""})
    assert r2.status_code == 400
    assert "6+ characters" in r2.get_json()["error"].lower()

    # Missing email / password entirely
    assert client.post("/api/register", json={}).status_code == 400

    # Password less than 6 characters
    r3 = client.post("/api/register", json={"email": "test@example.com", "password": "123"})
    assert r3.status_code == 400
    assert "6+ characters" in r3.get_json()["error"].lower()

    # Login with empty email/password
    r4 = client.post("/api/login", json={"email": "", "password": ""})
    assert r4.status_code in (400, 401)


def test_duplicate_register(client):
    register(client)
    assert register(client).status_code == 409


def test_protected_routes_need_token(client):
    assert client.get("/api/history").status_code == 401
    assert client.post("/api/analyze").status_code == 401


def test_history_endpoint_and_user_isolation(client):
    # Register user 1
    r1 = client.post("/api/register", json={"email": "user1@example.com", "password": "password123"})
    assert r1.status_code == 200
    tok1 = r1.get_json()["token"]

    # History should be empty initially
    h1 = client.get("/api/history", headers={"Authorization": f"Bearer {tok1}"})
    assert h1.status_code == 200
    assert h1.get_json()["history"] == []

    # Register user 2
    r2 = client.post("/api/register", json={"email": "user2@example.com", "password": "password456"})
    assert r2.status_code == 200
    tok2 = r2.get_json()["token"]

    # User 2 history is isolated and empty
    h2 = client.get("/api/history", headers={"Authorization": f"Bearer {tok2}"})
    assert h2.status_code == 200
    assert h2.get_json()["history"] == []

    # Invalid token rejected
    assert client.get("/api/history", headers={"Authorization": "Bearer badtoken"}).status_code == 401


def test_analyze_requires_inputs(client):
    tok = register(client).get_json()["token"]
    r = client.post("/api/analyze", headers={"Authorization": "Bearer " + tok}, data={"jd": "x"})
    assert r.status_code == 400


def test_llm_offline_fallbacks(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    s, fb = llm.evaluate("q", "short answer", "jd")
    assert 1 <= s <= 10 and fb
    assert len(llm.questions("r", "jd", ["docker"])) >= 4
