import os, json, re, requests


def ask(prompt):
    """Call Gemini. Returns None when no key is set or the call fails (app falls back to offline mode)."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    try:
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                          params={"key": key}, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=45)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None


def _json(t):
    try:
        return json.loads(re.sub(r"^```(?:json)?|```$", "", t.strip(), flags=re.M).strip())
    except Exception:
        return None


def suggestions(resume, jd, missing):
    t = ask(f"Resume:\n{resume[:4000]}\n\nJob description:\n{jd[:3000]}\n\nMissing skills: {', '.join(missing) or 'none'}.\n"
            "Give 4 short, concrete suggestions to tailor this resume to the job. One per line, starting with '- '.")
    if t:
        return t
    return ("- Add these skills if you genuinely have them: " + ", ".join(missing)) if missing else \
        "- Your resume covers the listed skills. Quantify your impact with numbers."


def questions(resume, jd, missing):
    j = _json(ask(f"Job description:\n{jd[:3000]}\n\nResume:\n{resume[:3000]}\n\nWrite 5 technical and 3 HR interview "
                  'questions for this role. Reply only with JSON: [{"type":"Technical","q":"..."}]') or "")
    if isinstance(j, list) and j:
        return j
    base = [{"type": "Technical", "q": f"Explain your experience with {s} and a problem you solved with it."}
            for s in (missing[:3] or ["your strongest skill"])]
    return base + [{"type": "HR", "q": "Tell me about yourself."},
                   {"type": "HR", "q": "Describe a team conflict and how you handled it."},
                   {"type": "HR", "q": "Why do you want this role?"}]


def evaluate(question, answer, jd):
    j = _json(ask(f"Job description:\n{jd[:2000]}\n\nQuestion: {question}\nCandidate answer: {answer}\n\n"
                  'Score the answer 1-10 and give 3 sentences of constructive feedback. Reply only with JSON: '
                  '{"score":7,"feedback":"..."}') or "")
    if isinstance(j, dict) and "score" in j:
        return max(1, min(10, int(j["score"]))), j.get("feedback", "")
    n = len(answer.split())
    return (3 if n < 20 else 5 if n < 50 else 6), \
        "Offline mode (no API key): only answer length was checked. Add a concrete example, the result, and the skills used."
