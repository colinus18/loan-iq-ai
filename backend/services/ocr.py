from pathlib import Path

import pytesseract
from PIL import Image


TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from an image using Tesseract OCR.

    Args:
        file_path: Path to the image.

    Returns:
        Extracted text.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {file_path}")

    supported_formats = {".png", ".jpg", ".jpeg"}

    if path.suffix.lower() not in supported_formats:
        raise ValueError(
            "Unsupported image format. "
            "Supported formats: PNG, JPG, JPEG."
        )

    with Image.open(path) as image:
        # Convert to RGB for consistent OCR processing
        image = image.convert("RGB")

        text = pytesseract.image_to_string(
            image,
            lang="eng"
        )

    return text.strip()