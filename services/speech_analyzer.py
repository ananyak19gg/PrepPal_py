import whisper
from typing import Dict
import os
import tempfile
from pathlib import Path

# Load Whisper model once
model = whisper.load_model("tiny")

def analyze_audio_chunk(audio_bytes: bytes, filename: str | None = None) -> Dict:
    """
    Transcribe audio chunk for real-time transcription
    Frontend sends audio chunks during interview
    """
    
    try:
        suffix = Path(filename or "audio.wav").suffix or ".wav"

        # Save bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        # Transcribe
        result = model.transcribe(tmp_path)
        
        # Cleanup
        os.remove(tmp_path)
        
        return {
            "success": True,
            "transcript": result["text"],
            "language": result.get("language", "en")
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
