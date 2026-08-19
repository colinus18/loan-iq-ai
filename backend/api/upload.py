from fastapi import APIRouter, File, Form, UploadFile

from services.file_storage import save_uploaded_file


router = APIRouter(
    prefix="/api/upload",
    tags=["Upload"]
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}


@router.post("")
async def upload_document(
    application_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a loan document.
    """

    filename = file.filename or ""

    extension = "." + filename.split(".")[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return {
            "status": "error",
            "message": (
                f"Unsupported file type: {extension}. "
                "Allowed: PDF, PNG, JPG, JPEG."
            )
        }

    saved_path = save_uploaded_file(
        file,
        application_id
    )

    return {
        "status": "uploaded",
        "application_id": application_id,
        "file_name": filename,
        "file_path": saved_path,
    }