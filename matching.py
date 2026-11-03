import re
from functools import lru_cache

# Expand common skill names and abbreviations before comparing resumes.
SKILL_GROUPS = {
    "python": ["python", "python3"],
    "machine learning": ["machine learning", "ml", "scikit learn", "scikit-learn"],
    "deep learning": ["deep learning", "dl"],
    "natural language processing": ["natural language processing", "nlp"],
    "flask": ["flask"],
    "django": ["django"],
    "sql": ["sql", "mysql", "postgresql", "postgres"],
    "nosql": ["nosql", "mongodb", "dynamodb"],
    "java": ["java"],
    "c++": ["c++", "cpp"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "reactjs"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "docker": ["docker", "containers", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud platform"],
    "terraform": ["terraform", "infrastructure as code", "iac"],
    "git": ["git", "github", "gitlab"],
    "linux": ["linux", "unix"],
    "rest api": ["rest api", "restful api", "rest apis"],
    "computer vision": ["computer vision", "opencv", "image processing"],
    "tensorflow": ["tensorflow", "keras"],
    "pytorch": ["pytorch", "torch"],
    "data analysis": ["data analysis", "data analytics", "pandas", "numpy"],
    "communication": ["communication", "stakeholder management"],
    "project management": ["project management", "agile", "scrum"],
    "solidworks": ["solidworks"],
    "ansys": ["ansys"],
    "matlab": ["matlab"],
}

EDUCATION_LEVELS = [
    ("phd", 1.00, ["phd", "doctorate", "doctoral"]),
    ("master's", 0.90, ["master", "m.tech", "mtech", "m.s.", "ms", "mba"]),
    ("bachelor's", 0.80, ["bachelor", "b.tech", "btech", "b.e.", "b.e", "b.sc", "bsc"]),
    ("diploma", 0.65, ["diploma", "associate degree"]),
]


def _normalise(text):
    return re.sub(r"\s+", " ", text.lower())


def extract_skills(text):
    normalized = _normalise(text)
    found = []
    for canonical, aliases in SKILL_GROUPS.items():
        for alias in aliases:
            # Word boundaries prevent matching e.g. "java" inside "javascript".
            pattern = r"(?<![a-z0-9+#])" + re.escape(alias) + r"(?![a-z0-9+#])"
            if re.search(pattern, normalized):
                found.append(canonical)
                break
    return sorted(set(found))


def education_score(text):
    normalized = _normalise(text)
    for _label, score, terms in EDUCATION_LEVELS:
        for term in terms:
            if re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", normalized):
                return score
    return 0.50


@lru_cache(maxsize=1)
def _load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def semantic_similarity(job_description, resume_text):
    """Return cosine similarity mapped to a 0-100 score."""
    try:
        import numpy as np
        model = _load_model()
        embeddings = model.encode([job_description, resume_text], normalize_embeddings=True)
        similarity = float(np.dot(embeddings[0], embeddings[1]))
        return max(0.0, min(100.0, similarity * 100))
    except Exception:
        # A lexical fallback keeps the application usable if the model cannot load.
        # Install sentence-transformers and allow its model download for SBERT matching.
        job_tokens = set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]+", job_description.lower()))
        resume_tokens = set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]+", resume_text.lower()))
        if not job_tokens:
            return 0.0
        return 100.0 * len(job_tokens & resume_tokens) / len(job_tokens)


def rank_candidates(job_description, candidates):
    job_skills = set(extract_skills(job_description))
    ranked = []

    for candidate in candidates:
        resume_text = candidate["text"]
        resume_skills = set(extract_skills(resume_text))
        matched = sorted(job_skills & resume_skills)
        missing = sorted(job_skills - resume_skills)

        semantic = semantic_similarity(job_description, resume_text)
        skill_score = (len(matched) / len(job_skills) * 100) if job_skills else 0.0
        education = education_score(resume_text) * 100
        overall = 0.60 * semantic + 0.30 * skill_score + 0.10 * education

        ranked.append({
            "name": candidate["name"],
            "overall_score": round(overall, 2),
            "semantic_score": round(semantic, 2),
            "skill_score": round(skill_score, 2),
            "education_score": round(education, 2),
            "matched_skills": matched,
            "missing_skills": missing,
            "resume_preview": re.sub(r"\s+", " ", resume_text).strip()[:260]
        })

    return sorted(ranked, key=lambda item: item["overall_score"], reverse=True)
