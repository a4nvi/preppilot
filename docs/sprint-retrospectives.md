# Sprint Retrospectives & Ceremony Logs

**Project:** PrepPilot  
**Course:** Fundamentals of Agile Software Development [26B16CS314]  
**Facilitated by Scrum Master:** Mokshi Mittal (Roll No: 2401030326, GitHub: @erica-maitri)  
**Team Members:** Aadya Mudgal (PO), Mokshi Mittal (SM), Jahnavi Singh (Dev), Shikhar Shukla (Dev), Aanvi Sawhney (QA)

---

## 1. Sprint 1 Retrospective (Foundation)
**Duration:** 2 Weeks  
**Sprint Goal:** Establish SQLite schema, secure user authentication API, resume upload, and foundational frontend layout.

### What Went Well
- Database schema (`users`, `analyses`, `answers`) designed and initialized cleanly in SQLite.
- Registration and login APIs operational with secure password hashing via `werkzeug.security`.
- Good communication within the team during sprint planning.

### What Could Be Improved
- Frontend Vite dev server (port 5173) experienced CORS connection errors when contacting the Flask API (port 5001).
- Lack of formalized pull request review guidelines leading to direct commit attempts.

### Action Items & Process Adjustments
1. Integrated `Flask-CORS` into `app.py` to allow cross-origin requests from the React client.
2. Established strict Git branching policy: all development restricted to `feature/*` branches with mandatory peer PR review.

---

## 2. Sprint 2 Retrospective (Core Features)
**Duration:** 2 Weeks  
**Sprint Goal:** Implement resume PDF parsing, resume-to-JD match scoring, and Gemini-based interview question generation.

### What Went Well
- PyPDF extraction reliably reads resume text without needing heavy external OCR libraries.
- Keyword matching algorithm in `matcher.py` successfully calculates match score and pinpoints missing skills.
- Frontend and backend integration for the analyzer view completed ahead of schedule.

### What Could Be Improved
- External Gemini API quota limits slowed down automated testing when running frequently.
- API payload response structures changed mid-sprint, requiring frontend adjustments.

### Action Items & Process Adjustments
1. Implemented offline fallbacks in `llm.py` so PyTest runs without requiring live API keys or internet access.
2. Standardized JSON response schemas across endpoints before coding starts.

---

## 3. Sprint 3 Retrospective (Completion & Quality)
**Duration:** 2 Weeks  
**Sprint Goal:** Complete answer evaluation, practice history dashboard, PyTest coverage, and CI pipeline setup.

### What Went Well
- Adopted Extreme Programming (XP) Driver/Navigator pair programming (Mokshi & Jahnavi).
- Successfully implemented Test-Driven Development (TDD) Red-Green cycle.
- GitHub Actions CI pipeline running automatically on all pushes and pull requests.

### What Could Be Improved
- Test coverage needed to be expanded to cover edge cases like empty inputs and cross-user data isolation.

### Action Items & Process Adjustments
1. Added full PyTest coverage for empty fields, case-insensitive duplicate registrations, and multi-user isolation on `/api/history`.
2. Verified all acceptance criteria against the Definition of Done (DoD).

---

## 4. Team Velocity Tracking

| Sprint | Story Points Planned | Story Points Completed | Velocity | Status |
|---|---|---|---|---|
| Sprint 1: Foundation | 16 | 16 | 16 | 100% Completed |
| Sprint 2: Core Features | 19 | 19 | 19 | 100% Completed |
| Sprint 3: Completion | 15 | 15 | 15 | 100% Completed |
| **Total** | **50** | **50** | **Avg: 16.7 pts/sprint** | **All Goals Met** |
