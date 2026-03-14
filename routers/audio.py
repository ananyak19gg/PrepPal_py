from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.speech_analyzer import analyze_audio_chunk

router = APIRouter(prefix="/api/analyze", tags=["audio"])

ALLOWED_AUDIO_TYPES = {"webm", "wav", "mp3", "m4a", "ogg", "mpeg"}
MAX_AUDIO_SIZE_BYTES = 15 * 1024 * 1024


@router.post("/audio")
async def analyze_audio_endpoint(file: UploadFile = File(...)):
    """
    Transcribe one recorded answer and return the transcript for the Next backend.
    """

    filename = file.filename or ""
    file_extension = Path(filename).suffix.lower().lstrip(".")

    if file_extension not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio type. Upload WEBM, WAV, MP3, M4A, OGG, or MPEG audio.",
        )

    try:
        audio_bytes = await file.read()

        if len(audio_bytes) > MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="Audio file is too large.")

        result = analyze_audio_chunk(audio_bytes, filename)

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))

        return {
            "success": True,
            "filename": filename,
            "transcript": result["transcript"],
            "language": result.get("language", "en"),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error transcribing audio: {str(exc)}",
        ) from exc
