# Smart Hiring Assistant with Semantic Search

An AI-powered applicant tracking system that evaluates resumes against a job description and ranks candidates using semantic relevance, technical skill alignment, and academic qualifications.

## Features

- **Semantic resume matching:** Uses Sentence-BERT (`all-MiniLM-L6-v2`) to compare the meaning of a job description with each resume.
- **Skill extraction:** Identifies technical and professional skills using a configurable skill dictionary with common aliases and keyword expansion.
- **Weighted candidate ranking:** Combines semantic similarity (60%), skill alignment (30%), and education (10%) into an overall match score.
- **Multi-format parsing:** Supports PDF, DOCX, and TXT resumes.
- **Batch processing:** Upload and evaluate multiple resumes against one job description.
- **Responsive interface:** Provides a clean candidate leaderboard with score breakdowns, matched skills, and skills to review.

## Technology Stack

- **Backend:** Python, Flask
- **NLP / Semantic Search:** Sentence-Transformers, Sentence-BERT
- **Resume Parsing:** PyPDF2, docx2txt
- **Frontend:** HTML, CSS, JavaScript

## Project Structure

```text
smart-hiring-assistant/
├── app.py
├── matching.py
├── resume_parser.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
└── uploads/
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/smart-hiring-assistant.git
cd smart-hiring-assistant
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Sentence-Transformers downloads the `all-MiniLM-L6-v2` model the first time semantic matching is used. An internet connection is required for the initial model download.

### 4. Run the application

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## Matching Methodology

Each resume receives three component scores:

| Component | Weight | Description |
|---|---:|---|
| Semantic relevance | 60% | Cosine similarity between normalized Sentence-BERT embeddings of the job description and resume |
| Skill alignment | 30% | Percentage of skills detected in the job description that are also found in the resume |
| Education | 10% | Heuristic score based on the highest recognized education level |

The overall score is calculated as:

```text
Overall Score = (0.60 × Semantic Score)
              + (0.30 × Skill Score)
              + (0.10 × Education Score)
```

All component scores are expressed on a 0–100 scale. The skill dictionary and education-level rules can be customized in `matching.py` to suit a particular role or hiring process.

If the Sentence-BERT model cannot be loaded, the application uses a lexical-overlap fallback for the semantic component. This fallback is intended for graceful operation and is not equivalent to embedding-based semantic matching.

## API

### `POST /api/match`

Accepts multipart form data:

| Field | Type | Description |
|---|---|---|
| `job_description` | Text | Job profile and requirements |
| `resumes` | Files | One or more PDF, DOCX, or TXT resumes |

Returns ranked candidates with overall and component scores, matched skills, missing skills, and a short resume preview.

## Configuration and Notes

- Maximum combined upload size: 15 MB.
- Supported file extensions: `.pdf`, `.docx`, `.txt`.
- Uploaded files are stored temporarily during parsing and deleted after processing.
- Scanned/image-only PDFs may require OCR before their text can be extracted.
- Education scoring is based on text matching and should be adapted to the organization's qualification criteria.
- Resume rankings should support, not replace, structured human review. Validate the scoring approach for the role and avoid using protected or irrelevant personal attributes in hiring decisions.

## License

This project is available under the MIT License. Add a `LICENSE` file if you intend to distribute it under that license.
