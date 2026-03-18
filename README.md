PrepPal Python Backend
AI microservice for resume parsing, speech transcription, and video analysis in PrepPal's interview platform.
🔗 Live API
https://aaaaaaaannnnnnnnnyyyyyyyyyyy-interview.hf.space
Architecture
Stateless FastAPI service processing multimodal interview data through specialized ML pipelines.
Flow: Frontend → Python API → ML Models → JSON → Next.js → MongoDB
Endpoints
EndpointInputOutputPOST /api/analyze/resumePDF/ImageExtracted textPOST /api/analyze/audioAudio fileTranscriptPOST /api/analyze/videoVideo filePosture, gaze, engagement scores
Tech Stack
Framework: FastAPI
ML Models: Whisper (tiny), OpenCV, EasyOCR, pdfplumber
Deployment: Docker on Hugging Face Spaces
Key Design Decisions
Separate microservice: Isolates compute-heavy ML from Next.js, enables independent scaling
Whisper tiny: 150MB RAM vs 500MB (base) - necessary for free tier deployment
Frame sampling: Analyzes every 10th frame for speed without significant accuracy loss
Pre-loaded models: Downloaded during Docker build to avoid runtime network failures
Local Setup
bashgit clone https://github.com/ananyak19gg/python_lib_interview.git
cd python_lib_interview
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python main.py
Integration Example
javascriptconst formData = new FormData();
formData.append('file', file);

const res = await fetch('https://your-api.hf.space/api/analyze/resume', {
    method: 'POST',
    body: formData
});
```

## Project Structure
```
routers/     # API endpoints
services/    # ML analysis logic
main.py      # FastAPI app
Dockerfile   # Container config
Performance

Resume: 0.5-2s
Audio: ~0.3x real-time
Video: ~0.1s per frame

Built by Team Xtract | MIT License
