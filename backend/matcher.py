import re

SKILLS = ["python", "java", "javascript", "typescript", "c++", "c#", "sql", "mysql", "postgresql", "mongodb", "sqlite",
    "redis", "react", "angular", "vue", "node.js", "express", "flask", "django", "fastapi", "spring", "html", "css",
    "tailwind", "rest api", "graphql", "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "ci/cd", "linux",
    "jenkins", "machine learning", "deep learning", "nlp", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "data analysis", "power bi", "tableau", "agile", "scrum", "testing", "pytest", "junit", "selenium", "api",
    "microservices", "data structures", "algorithms", "oop", "dbms", "operating systems", "computer networks",
    "communication", "leadership", "teamwork", "problem solving"]


def _find(text):
    t = text.lower()
    return {s for s in SKILLS if re.search(r"(?<![a-z0-9+#])" + re.escape(s) + r"(?![a-z0-9+#])", t)}


def compare(resume, jd):
    need, have = _find(jd), _find(resume)
    matched, missing = sorted(need & have), sorted(need - have)
    score = round(100 * len(matched) / len(need)) if need else 0
    return {"score": score, "matched": matched, "missing": missing}
