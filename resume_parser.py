from PyPDF2 import PdfReader
import docx2txt


def extract_text(file_path: str, extension: str) -> str:
    """Extract text from PDF, DOCX, or TXT resume files."""
    extension = extension.lower()
    if extension == "pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if extension == "docx":
        return docx2txt.process(file_path) or ""
    if extension == "txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            return file.read()
    raise ValueError("Unsupported resume format")
