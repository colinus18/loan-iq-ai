from pathlib import Path
import shutil


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"


def save_uploaded_file(file, application_id: str) -> str:
    """
    Save an uploaded file under the application ID.

    Returns:
        Absolute path of the saved file.
    """

    application_dir = UPLOAD_DIR / application_id
    application_dir.mkdir(parents=True, exist_ok=True)

    file_path = application_dir / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return str(file_path)