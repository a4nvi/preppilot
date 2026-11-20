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


def test_duplicate_register(client):
    register(client)
    assert register(client).status_code == 409


def test_protected_routes_need_token(client):
    assert client.get("/api/history").status_code == 401
    assert client.post("/api/analyze").status_code == 401


def test_analyze_requires_inputs(client):
    tok = register(client).get_json()["token"]
    r = client.post("/api/analyze", headers={"Authorization": "Bearer " + tok}, data={"jd": "x"})
    assert r.status_code == 400


def test_llm_offline_fallbacks(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    s, fb = llm.evaluate("q", "short answer", "jd")
    assert 1 <= s <= 10 and fb
    assert len(llm.questions("r", "jd", ["docker"])) >= 4
