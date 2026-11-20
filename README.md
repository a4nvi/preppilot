# PrepPilot: AI-Powered Resume Analyzer and Interview Prep

Flask + SQLite backend, React + Tailwind frontend, Gemini for questions and feedback (works offline without a key).

## Run

```
cd backend && pip install -r requirements.txt && cp .env.example .env   # add GEMINI_API_KEY
export $(cat .env | xargs) && python app.py        # http://localhost:5001
cd frontend && npm install && npm run dev          # http://localhost:5173
cd backend && pytest -q                            # tests
```

## Deploy

Backend (Render): root `backend`, start `gunicorn "app:create_app()"`, set GEMINI_API_KEY and SECRET_KEY.
Frontend (Vercel): root `frontend`, set `VITE_API_URL` to the Render URL.

## Backlog coverage

US1 auth, US2 PDF upload, US3 JD input, US4 score and skill gaps, US5 questions, US6 feedback, US7 history, US8 report download.
