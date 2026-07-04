import PyPDF2
import docx

def extract_text_from_pdf(file) -> str:
    """Extract text from a PDF file object."""
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def extract_text_from_docx(file) -> str:
    """Extract text from a DOCX file object."""
    doc = docx.Document(file)
    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return text.strip()

def extract_resume_text(uploaded_file) -> str:
    """
    Detects file type by extension and extracts text accordingly.
    'uploaded_file' should be a file-like object with a .name attribute
    (this matches what Streamlit's file_uploader gives us later).
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX.")