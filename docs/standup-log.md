# Standup Log

## Sprint 1: Foundation

- Done: project setup, database schema, register/login, PDF upload and text extraction
- Next: connect upload to the UI, start job description input
- Blockers: team members were pushing directly to `main`. Resolved by the Scrum Master setting a rule that everyone works on their own feature branch and another member reviews the PR before merging.

## Sprint 2: Core Features

- Done: job description input, matcher and skill-gap report, question generation
- Next: answer evaluation, history
- Blockers: the React frontend (port 5173) could not call the Flask backend (port 5001) because the browser blocked the requests with a CORS error. Resolved by adding Flask-CORS in `app.py` and correcting the API URL.

## Sprint 3: Completion

- Done: answer feedback, history dashboard, tests, CI
- Next: documentation, demo
- Blockers: automated tests hit Gemini API rate limits and failed. Resolved by adding offline fallback responses in `llm.py`, so tests run without using API credits.
