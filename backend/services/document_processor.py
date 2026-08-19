from pathlib import Path

from services.ocr import extract_text_from_image
from services.pdf_reader import extract_text_from_pdf


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}


def process_document(file_path: str) -> dict:
    """
    Process a PDF or image document and extract its text.

    Returns:
        Dictionary containing extracted text and processing metadata.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    # PDF processing
    if extension == ".pdf":
        text = extract_text_from_pdf(str(path))

        return {
            "file_name": path.name,
            "file_type": "PDF",
            "processing_method": "PDF_TEXT",
            "status": "completed",
            "text": text,
        }

    # Image processing
    text = extract_text_from_image(str(path))

    return {
        "file_name": path.name,
        "file_type": "IMAGE",
        "processing_method": "OCR",
        "status": "completed",
        "text": text,
    }