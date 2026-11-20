import os, json, sqlite3
from flask import Flask, request, jsonify, g, Response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature
from pypdf import PdfReader
import matcher, llm

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, pw TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS analyses(id INTEGER PRIMARY KEY, user_id INT, jd TEXT, resume TEXT, score INT,
  matched TEXT, missing TEXT, tips TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS answers(id INTEGER PRIMARY KEY, analysis_id INT, user_id INT, question TEXT, answer TEXT,
  score INT, feedback TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
"""


def create_app(db_path=None):
    app = Flask(__name__)
    CORS(app)
    path = db_path or os.environ.get("DB_PATH", "prep.db")
    ser = URLSafeTimedSerializer(os.environ.get("SECRET_KEY", "dev-secret"))

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(path)
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def _close(_):
        d = g.pop("db", None)
        if d:
            d.close()

    with app.app_context():
        db().executescript(SCHEMA)

    def uid():
        try:
            tok = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
            return ser.loads(tok, max_age=7 * 86400) if tok else None
        except Exception:
            return None

    def err(m, c=400):
        return jsonify(error=m), c

    def own(aid, u):
        return db().execute("SELECT * FROM analyses WHERE id=? AND user_id=?", (aid, u)).fetchone()

    # ---- US1: register / login
    @app.post("/api/register")
    def register():
        d = request.get_json(force=True) or {}
        e = (d.get("email") or "").strip().lower()
        p = d.get("password") or ""
        if "@" not in e or len(p) < 6:
            return err("Enter a valid email and a password of 6+ characters.")
        try:
            cur = db().execute("INSERT INTO users(email,pw) VALUES(?,?)", (e, generate_password_hash(p)))
            db().commit()
        except sqlite3.IntegrityError:
            return err("That email is already registered.", 409)
        return jsonify(token=ser.dumps(cur.lastrowid))

    @app.post("/api/login")
    def login():
        d = request.get_json(force=True) or {}
        e = (d.get("email") or "").strip().lower()
        p = d.get("password") or ""
        if not e or not p:
            return err("Email and password are required.", 400)
        u = db().execute("SELECT * FROM users WHERE email=?", (e,)).fetchone()
        if not u or not check_password_hash(u["pw"], p):
            return err("Wrong email or password.", 401)
        return jsonify(token=ser.dumps(u["id"]))

    # ---- US2-US4: upload resume + JD, match score, skill gaps
    @app.post("/api/analyze")
    def analyze():
        u = uid()
        if not u:
            return err("Log in first.", 401)
        f, jd = request.files.get("resume"), request.form.get("jd", "").strip()
        if not f or not jd:
            return err("Upload a resume PDF and paste a job description.")
        try:
            text = "\n".join(p.extract_text() or "" for p in PdfReader(f).pages)
        except Exception:
            return err("Could not read that PDF.")
        if not text.strip():
            return err("No text found in the PDF. Scanned resumes are not supported.")
        r = matcher.compare(text, jd)
        tips = llm.suggestions(text, jd, r["missing"])
        cur = db().execute("INSERT INTO analyses(user_id,jd,resume,score,matched,missing,tips) VALUES(?,?,?,?,?,?,?)",
                           (u, jd, text, r["score"], json.dumps(r["matched"]), json.dumps(r["missing"]), tips))
        db().commit()
        return jsonify(id=cur.lastrowid, tips=tips, **r)

    # ---- US5: questions
    @app.post("/api/questions")
    def questions():
        u = uid()
        if not u:
            return err("Log in first.", 401)
        a = own((request.get_json(force=True) or {}).get("analysis_id"), u)
        if not a:
            return err("Analysis not found.", 404)
        return jsonify(questions=llm.questions(a["resume"], a["jd"], json.loads(a["missing"])))

    # ---- US6: answer feedback
    @app.post("/api/feedback")
    def feedback():
        u = uid()
        if not u:
            return err("Log in first.", 401)
        d = request.get_json(force=True)
        a = own(d.get("analysis_id"), u)
        if not a or not d.get("answer", "").strip():
            return err("Write an answer first.")
        s, fb = llm.evaluate(d.get("question", ""), d["answer"], a["jd"])
        db().execute("INSERT INTO answers(analysis_id,user_id,question,answer,score,feedback) VALUES(?,?,?,?,?,?)",
                     (a["id"], u, d.get("question", ""), d["answer"], s, fb))
        db().commit()
        return jsonify(score=s, feedback=fb)

    # ---- US7: history
    @app.get("/api/history")
    def history():
        u = uid()
        if not u:
            return err("Log in first.", 401)
        rows = db().execute("SELECT id,score,created,substr(jd,1,90) AS jd FROM analyses WHERE user_id=? ORDER BY id DESC", (u,)).fetchall()
        out = []
        for r in rows:
            ans = db().execute("SELECT question,answer,score,feedback FROM answers WHERE analysis_id=? ORDER BY id", (r["id"],)).fetchall()
            out.append({**dict(r), "answers": [dict(x) for x in ans]})
        return jsonify(history=out)

    # ---- US8: downloadable report
    @app.get("/api/report/<int:aid>")
    def report(aid):
        u = uid()
        if not u:
            return err("Log in first.", 401)
        a = own(aid, u)
        if not a:
            return err("Analysis not found.", 404)
        txt = (f"PrepPilot report #{aid}\nMatch score: {a['score']}%\nMatched: {', '.join(json.loads(a['matched']))}\n"
               f"Missing: {', '.join(json.loads(a['missing']))}\n\nSuggestions:\n{a['tips']}\n")
        return Response(txt, mimetype="text/plain", headers={"Content-Disposition": f"attachment; filename=report-{aid}.txt"})

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5001)
