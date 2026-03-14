import os
import shutil
import time
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.video_analyzer import analyze_video

router = APIRouter(prefix="/api/analyze", tags=["video"])

ALLOWED_VIDEO_TYPES = {"webm", "mp4", "mov"}
MAX_VIDEO_SIZE_BYTES = 100 * 1024 * 1024


def _get_file_size(upload: UploadFile) -> int:
    upload.file.seek(0, os.SEEK_END)
    size = upload.file.tell()
    upload.file.seek(0)
    return size


@router.post("/video")
async def analyze_video_endpoint(file: UploadFile = File(...)):
    """
    Analyze video for posture, gaze, and engagement.
    """

    filename = file.filename or ""
    file_extension = Path(filename).suffix.lower().lstrip(".")

    if file_extension not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported video type. Upload WEBM, MP4, or MOV video.",
        )

    if _get_file_size(file) > MAX_VIDEO_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Video file is too large.")

    os.makedirs("uploads", exist_ok=True)
    temp_filename = f"{uuid4().hex}.{file_extension}"
    temp_path = Path("uploads") / temp_filename

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        results = analyze_video(str(temp_path))

        if not results.get("success"):
            raise HTTPException(
                status_code=500,
                detail=results.get("error", "Analysis failed"),
            )

        return {
            "success": True,
            "filename": filename,
            "analysis": results,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing video: {str(exc)}",
        ) from exc
    finally:
        if temp_path.exists():
            try:
                time.sleep(1)
                temp_path.unlink()
            except Exception:
                pass
