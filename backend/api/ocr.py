from pathlib import Path

from fastapi import APIRouter, HTTPException

from services.document_processor import process_document


router = APIRouter(
    prefix="/api/ocr",
    tags=["OCR"]
)


@router.post("")
async def process_ocr(file_path: str):
    """
    Process an already uploaded document.
    """

    path = Path(file_path)

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    try:
        result = process_document(str(path))

        return {
            "status": "completed",
            "result": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {exc}"
        )