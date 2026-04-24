"""PDF parsing helpers."""

from PyPDF2 import PdfReader

from utils.cleaner import normalize_text


def extract_text_from_pdf(file) -> str:
    """Extract and clean plain text from a PDF file object.

    Returns an empty string if the file is invalid or has no extractable text.
    """
    if file is None:
        return ""

    try:
        reader = PdfReader(file)
    except Exception:
        return ""

    pages_text = []
    for page in reader.pages:
        try:
            pages_text.append(page.extract_text() or "")
        except Exception:
            pages_text.append("")

    raw_text = " ".join(pages_text).strip()
    return normalize_text(raw_text)
