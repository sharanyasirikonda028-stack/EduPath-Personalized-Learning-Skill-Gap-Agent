"""Extracts raw text from an uploaded PDF resume."""

from io import BytesIO
import pdfplumber


def extract_text_from_pdf(uploaded_file) -> str:
    """uploaded_file is a Streamlit UploadedFile object."""
    text_chunks = []
    with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    return "\n".join(text_chunks)
