# PrepPilot: Scrum Master Process & Contribution Report

**Course:** Fundamentals of Agile Software Development [26B16CS314]  
**Institution:** Jaypee Institute of Information Technology (JIIT), Noida — B.Tech V Semester  
**Scrum Master:** Mokshi Mittal (Roll No: 2401030326)  
**GitHub Username:** [@erica-maitri](https://github.com/erica-maitri)  
**Repository:** [github.com/a4nvi/preppilot](https://github.com/a4nvi/preppilot)  
**Team Members:**  
- **Aadya Mudgal** (Roll No: 2401030368) — Product Owner / Frontend  
- **Mokshi Mittal** (Roll No: 2401030326) — Scrum Master / DB & Auth  
- **Jahnavi Singh** (Roll No: 2401030367) — Developer / APIs & Resume Parsing  
- **Shikhar Shukla** (Roll No: 2401030364) — Developer / LLM Integration  
- **Aanvi Sawhney** (Roll No: 2401030351) — QA & Documentation  

---

## 1. Executive Summary & Scrum Master Role

As the **Scrum Master** for the PrepPilot project, my core responsibility was not to act as a traditional project manager, but as a **servant-leader** and Agile coach for the team. My dual focus was:
1. **Agile Process Facilitation:** Ensuring adherence to Scrum principles, facilitating all Scrum ceremonies (Planning, Daily Standups, Review, and Retrospectives), tracking team velocity and sprint burndown, eliminating blockers, and maintaining a healthy collaborative environment.
2. **Extreme Programming (XP) & Quality Engineering:** Enforcing pair programming (Driver/Navigator approach), Test-Driven Development (TDD), branch hygiene, small incremental commits, and mandatory peer reviews before merging pull requests.
3. **Hands-on Technical Ownership:** Designing and implementing the database models (SQLite), user authentication REST endpoints (JWT token serialization and password hashing), and the PyTest automated test suite for authentication and history tracking.

---

## 2. Scrum Ceremonies Facilitated

Throughout our three 2-week sprints, I facilitated all key Scrum events to keep the team aligned and productive:

### 2.1 Sprint Planning
- **Sprint 1 (Foundation):** Coordinated with Product Owner Aadya Mudgal to define Sprint Goal 1 (*Establish baseline architecture, authentication, and PDF extraction*). Sized user stories using Planning Poker (Story Points: US1 = 8 points split across Frontend and Backend, US2 = 8 points).
- **Sprint 2 (Core Features):** Defined Sprint Goal 2 (*Resume-to-JD matching and interview question generation*). Mapped dependencies between Jahnavi's PDF extraction/matcher and Shikhar's LLM question prompt pipeline.
- **Sprint 3 (Completion & Polish):** Defined Sprint Goal 3 (*Evaluation feedback, practice history, and test coverage*). Prioritized testing, CI pipeline with GitHub Actions, and responsive UI polish.

### 2.2 Daily Stand-ups (Daily Scrum)
Conducted daily check-ins (15 minutes maximum) structured around the three classic questions:
1. *What did you accomplish yesterday?*
2. *What do you plan to accomplish today?*
3. *Are there any blockers or impediments in your way?*

### 2.3 Impediment Removal (Key Blockers Solved)
- **Blocker 1 (CORS & Port Mismatch):** Frontend (Vite on port 5173) was getting CORS errors calling the Flask API on port 5001.  
  *Resolution:* Added `flask_cors.CORS` in `app.py` and configured proper API URL base path in `.env`.
- **Blocker 2 (Gemini API Rate Limiting / Offline Mode):** Developers experienced API key quota exhaustion during testing.  
  *Resolution:* Ensured mock fallbacks in `llm.py` so local unit tests and PyTest can run completely offline without spending API quota.
- **Blocker 3 (Merge Conflicts & Overlapping Commits):** Team was initially tempted to push directly to `main`.  
  *Resolution:* Enforced a strict branch protection policy: feature branches (`feature/auth-tests`, `feature/analyze-test`, `feature/frontend-polish`, `feature/llm-fallback`) with pull requests reviewed by another peer.

### 2.4 Sprint Review & Demo
- Coordinated end-of-sprint demonstrations showing working software to the Product Owner against acceptance criteria.
- Validated that each deliverable met the team's agreed **Definition of Done (DoD)** before marking tasks as `Done` in `sprint-backlog.md`.

### 2.5 Sprint Retrospectives
Documented lessons learned and continuous improvement items:
- *What went well:* Clean separation of concerns between Flask backend and Vite React frontend; fast feedback loops with PyTest.
- *What to improve:* More granular story point estimation for complex LLM prompt testing; earlier agreement on API JSON payload contracts.
- *Action item:* Adopt strict TDD Red-Green-Refactor commits during pair programming.

---

## 3. Sprint-by-Sprint Contributions Breakdown

| Sprint | Goal | Scrum Master Facilitation | Technical Deliverables (Mokshi) |
|---|---|---|---|
| **Sprint 1: Foundation** | Setup project, auth API, resume upload | Facilitated Sprint Planning; established GitHub repo rules and sprint backlog; unblocked CORS setup. | Database schema design (`users`, `analyses`, `answers`); `/api/register` and `/api/login` endpoints with secure password hashing (`generate_password_hash`). |
| **Sprint 2: Core Features** | Resume-to-JD matching, LLM questions | Tracked velocity; held daily standups; managed dependencies between parsing API and matcher logic. | Designed relational link between user sessions and analyses in SQLite (`user_id` foreign reference); assisted with schema integrity. |
| **Sprint 3: Completion** | History dashboard, feedback, full testing | Organized XP Pair Programming session with Jahnavi; established Definition of Done; enforced CI pass on PRs. | `/api/history` endpoint with user isolation; comprehensive PyTest suite (`feature/auth-tests`); TDD Red-Green commit pairs. |

---

## 4. Extreme Programming (XP) Practices Enforced

To satisfy the XP requirements of the curriculum, I spearheaded the adoption of two key practices:

### 4.1 Pair Programming (Driver / Navigator Approach)
- Partnered with **Jahnavi Singh** for pair programming sessions.
- **Session Structure:**
  - In Task 1: Mokshi acted as **Driver** (writing the code/test) while Jahnavi acted as **Navigator** (reviewing logic, edge cases, and test assertions in real time).
  - In Task 2: Roles swapped to ensure shared code ownership and cross-pollination of knowledge across backend endpoints.

### 4.2 Test-Driven Development (TDD)
- Enforced the strict **Red-Green-Refactor** workflow:
  1. **Red Stage:** Write a failing test first that specifies expected behavior (e.g., rejecting registrations with missing fields or passwords < 6 characters). Commit with message: `test: add failing test for ...`.
  2. **Green Stage:** Write minimal code to pass the test. Commit with message: `feat: implement ...`.
  3. **Refactor Stage:** Clean up formatting, improve error messages, and ensure no regressions.

---

## 5. Technical Deliverables Owned by Mokshi

### 5.1 Database Architecture (`prep.db`)
Designed lightweight, reliable SQLite relational schema:
- `users`: `id`, `email UNIQUE`, `pw` (hashed)
- `analyses`: `id`, `user_id`, `jd`, `resume`, `score`, `matched`, `missing`, `tips`, `created`
- `answers`: `id`, `analysis_id`, `user_id`, `question`, `answer`, `score`, `feedback`, `created`

### 5.2 Authentication & History Endpoints
- **JWT / Serializer Security:** Implemented `itsdangerous.URLSafeTimedSerializer` for stateless, signed session tokens with 7-day expiration.
- **Route Protection:** Built user verification decorators/helpers (`uid()`) ensuring unauthorized requests return `401 Unauthorized`.
- **History Isolation:** Ensured `/api/history` filters strictly by the authenticated user's ID (`WHERE user_id=?`), protecting user privacy.

### 5.3 Automated Testing Suite (`tests/test_app.py`)
Authored PyTest test cases:
1. `test_duplicate_register`: Ensures duplicate email registration raises HTTP `409 Conflict`.
2. `test_register_validation`: Ensures empty email, missing `@`, or short passwords (<6 characters) raise HTTP `400 Bad Request`.
3. `test_login_invalid_credentials`: Verifies correct rejection with HTTP `401 Unauthorized`.
4. `test_history_isolation`: Validates that user analysis history is correctly stored, retrieved, and isolated from other users.

---

## 6. Definition of Done (DoD) Checklist

As Scrum Master, I enforced that a user story or task is only marked **"Done"** when:
- [x] Code is written on a dedicated feature branch (`feature/*`).
- [x] Associated unit tests are written and passing (`python -m pytest` passes 100%).
- [x] No lint or terminal errors on build.
- [x] Pull Request is opened with a descriptive summary of changes.
- [x] Peer review is completed and approved by another team member.
- [x] CI workflow (GitHub Actions) runs green on merge to `main`.
