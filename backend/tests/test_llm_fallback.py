import requests
import llm


def test_ask_returns_none_on_timeout(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

    def boom(*a, **k):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(llm.requests, "post", boom)  # mocked LLM that always times out
    assert llm.ask("hello") is None


def test_features_fall_back_when_llm_fails(monkeypatch):
    monkeypatch.setattr(llm, "ask", lambda prompt: None)  # mocked LLM error
    assert llm.suggestions("resume", "jd", ["docker"]).startswith("- Add these skills")
    assert len(llm.questions("resume", "jd", ["docker"])) >= 4
    score, fb = llm.evaluate("q", "short answer", "jd")
    assert 1 <= score <= 10 and "busy or unreachable" in fb


def test_evaluate_uses_mocked_llm_answer(monkeypatch):
    monkeypatch.setattr(llm, "ask", lambda prompt: '{"score": 8, "feedback": "Good example."}')
    assert llm.evaluate("q", "a long answer", "jd") == (8, "Good example.")


def test_feedback_endpoint_shows_friendly_message_when_llm_down(tmp_path, monkeypatch):
    from app import create_app
    monkeypatch.setattr(llm, "ask", lambda prompt: None)
    c = create_app(str(tmp_path / "t.db")).test_client()
    tok = c.post("/api/register", json={"email": "a@b.com", "password": "secret1"}).get_json()["token"]
    h = {"Authorization": "Bearer " + tok}
    import sqlite3
    con = sqlite3.connect(str(tmp_path / "t.db"))
    con.execute("INSERT INTO analyses(user_id,jd,resume,score,matched,missing,tips) VALUES(1,'jd','r',50,'[]','[]','t')")
    con.commit()
    r = c.post("/api/feedback", headers=h, json={"analysis_id": 1, "question": "q", "answer": "my answer"})
    assert r.status_code == 200
    assert "try again" in r.get_json()["feedback"].lower()
