import os
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.resume_analyzer import (
    extract_text_from_image,
    extract_text_from_pdf,
    structure_resume_data,
)

router = APIRouter(prefix="/api/analyze", tags=["resume"])

ALLOWED_RESUME_TYPES = {"pdf", "jpeg", "jpg", "png"}
MAX_RESUME_SIZE_BYTES = 10 * 1024 * 1024


def _get_file_size(upload: UploadFile) -> int:
    upload.file.seek(0, os.SEEK_END)
    size = upload.file.tell()
    upload.file.seek(0)
    return size


@router.post("/resume")
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    filename = file.filename or ""
    file_extension = Path(filename).suffix.lower().lstrip(".")

    if file_extension not in ALLOWED_RESUME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported resume type. Upload a PDF, PNG, JPG, or JPEG file.",
        )

    if _get_file_size(file) > MAX_RESUME_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Resume file is too large.")

    os.makedirs("uploads", exist_ok=True)
    temp_filename = f"{uuid4().hex}.{file_extension}"
    temp_path = Path("uploads") / temp_filename

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        if file_extension == "pdf":
            resume_text = extract_text_from_pdf(str(temp_path))
        else:
            resume_text = extract_text_from_image(str(temp_path))

        analysis = structure_resume_data(resume_text)

        return {
            "success": True,
            "filename": filename,
            "resumeText": resume_text,
            "wordCount": analysis["wordCount"],
            "characterCount": analysis["characterCount"],
            "analysis": analysis,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(exc)}",
        ) from exc
    finally:
        if temp_path.exists():
            temp_path.unlink()
