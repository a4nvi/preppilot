# Sprint Reviews and Retrospectives

## Sprint 1

- Review: demoed registration, login and resume upload; accepted by the Product Owner
- Went well: clear split between frontend and backend work
- Didn't go well: some members pushed directly to `main`, which risked unreviewed changes
- Change: everyone works on a feature branch, and another member reviews every PR before it is merged

## Sprint 2

- Review: demoed match score, skill gaps and interview questions
- Went well: the matcher and question generation worked end to end once the frontend and backend were connected
- Didn't go well: CORS errors blocked the frontend from reaching the backend because the ports and API URL were not agreed early
- Change: agree on ports, API URLs and CORS configuration at the start of integration work

## Sprint 3

- Review: demoed answer feedback, history and the full user flow
- Went well: backend tests pass and CI runs green on every push
- Didn't go well: tests depended on the live Gemini API and hit rate limits
- Change: tests run against offline fallback responses instead of the real LLM, so they are fast, free and reliable
