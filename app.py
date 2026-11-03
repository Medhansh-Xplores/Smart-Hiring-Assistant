import os
import uuid
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from resume_parser import extract_text
from matching import rank_candidates

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/match", methods=["POST"])
def match_resumes():
    job_description = request.form.get("job_description", "").strip()
    if len(job_description) < 20:
        return jsonify({"error": "Please provide a job description with at least 20 characters."}), 400

    uploaded_files = request.files.getlist("resumes")
    if not uploaded_files or not any(f.filename for f in uploaded_files):
        return jsonify({"error": "Upload at least one resume."}), 400

    candidates = []
    errors = []

    for file in uploaded_files:
        if not file.filename:
            continue
        original_name = secure_filename(file.filename)
        if not allowed_file(original_name):
            errors.append(f"{original_name}: unsupported file type")
            continue

        # Use a temporary unique name to avoid collisions between uploads.
        extension = original_name.rsplit(".", 1)[1].lower()
        temp_name = f"{uuid.uuid4().hex}.{extension}"
        path = os.path.join(app.config["UPLOAD_FOLDER"], temp_name)
        try:
            file.save(path)
            text = extract_text(path, extension)
            if text.strip():
                candidates.append({"name": original_name, "text": text})
            else:
                errors.append(f"{original_name}: no readable text found")
        except Exception as exc:
            errors.append(f"{original_name}: could not parse file ({str(exc)[:100]})")
        finally:
            if os.path.exists(path):
                os.remove(path)

    if not candidates:
        return jsonify({"error": "No readable resumes were found.", "details": errors}), 400

    try:
        results = rank_candidates(job_description, candidates)
    except Exception as exc:
        app.logger.exception("Resume matching failed")
        return jsonify({"error": "Matching failed. Please try again.", "details": str(exc)[:200]}), 500

    return jsonify({"results": results, "errors": errors})


@app.errorhandler(RequestEntityTooLarge)
def file_too_large(_error):
    return jsonify({"error": "The total upload size exceeds 15 MB."}), 413


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
            host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
