# PrepPal Python Backend

AI microservice powering resume parsing, speech transcription, and video analysis for PrepPal's adaptive interview platform.

## 🔗 API Endpoint
`https://aaaaaaaannnnnnnnnyyyyyyyyyyy-interview.hf.space`

## Architecture Overview

This service operates as a stateless microservice, receiving multimodal data from the Next.js frontend, processing it through specialized ML pipelines, and returning structured analysis.

**Data Flow:**
```
Frontend → Python API → ML Models → Structured Output → Frontend → MongoDB
```

The service handles three distinct analysis pipelines:

### 1. Resume Analysis Pipeline
Accepts PDF or image files, extracts textual content using pdfplumber (for PDFs) or EasyOCR (for images). Returns raw text for the Next.js backend to parse via LLM for question generation.

**Technical approach:** Optical character recognition with preprocessing (contrast enhancement, grayscale conversion) to improve accuracy on varied document quality.

### 2. Audio Transcription Pipeline  
Processes audio chunks or complete recordings through OpenAI's Whisper model (tiny variant for memory efficiency). Outputs timestamped transcripts for real-time cross-questioning.

**Model choice:** Whisper tiny balances accuracy (~85%) with RAM constraints (<200MB), critical for free-tier deployment.

### 3. Video Analysis Pipeline
Extracts frames from video, applies computer vision models to detect:
- **Face visibility:** Haar Cascade detection across frames
- **Posture:** Body landmark positioning via frame analysis
- **Gaze direction:** Eye detection and facial orientation
- **Engagement score:** Weighted combination of above metrics

**Optimization:** Processes every 10th frame to reduce compute time while maintaining statistical validity.

## Technical Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | FastAPI | Async request handling, auto-generated docs |
| ML Models | Whisper, OpenCV, EasyOCR | Speech, vision, OCR processing |
| Deployment | Docker on HF Spaces | Containerized deployment with model pre-loading |
| API Design | RESTful multipart/form-data | Standard file upload protocol |

## Design Decisions

**Why separate microservice?**
- Isolates compute-heavy ML operations from Next.js server
- Independent scaling and deployment
- Language-appropriate: Python for ML, TypeScript for business logic

**Why Whisper tiny over base/small?**
- RAM: 150MB vs 500MB+ (fits free tier limits)
- Latency: ~2x faster transcription
- Accuracy trade-off acceptable for interview context

**Why lazy model loading considered but rejected?**
- Initial attempt to load models on-demand failed due to network timeouts during download
- Solution: Pre-download during Docker build phase ensures models are baked into image

## Deployment Architecture

**Build process:**
1. Base Python 3.11 slim image
2. Install system dependencies (ffmpeg, OpenGL)
3. Install Python packages
4. Pre-download ML models (prevents runtime download failures)
5. Expose port 7860 (Hugging Face standard)

**Runtime:**
- Stateless design: No session management, all data ephemeral
- File lifecycle: Upload → Process → Delete (prevents storage bloat)
- CORS: Wildcard allowed for hackathon (would restrict in production)

## API Specifications

### POST /api/analyze/resume
**Input:** `multipart/form-data` with file field  
**Processing:** PDF extraction OR OCR → text cleaning  
**Output:**
```json
{
  "success": true,
  "extractedText": "string",
  "wordCount": 450
}
```

### POST /api/analyze/audio  
**Input:** Audio file (WAV/MP3/WebM)  
**Processing:** Whisper transcription  
**Output:**
```json
{
  "success": true,
  "transcript": "string",
  "language": "en"
}
```

### POST /api/analyze/video
**Input:** Video file (MP4/WebM)  
**Processing:** Frame sampling → CV detection → scoring  
**Output:**
```json
{
  "success": true,
  "faceVisibility": 85.5,
  "postureScore": 78.2,
  "gazeScore": 82.0,
  "engagementScore": 81.9,
  "totalFrames": 1200
}
```

## Performance Characteristics

- **Resume parsing:** 0.5-2s depending on file size
- **Audio transcription:** ~0.3x real-time (10s audio = 3s processing)
- **Video analysis:** ~0.1s per analyzed frame (1 min video = ~6s)

## Integration with PrepPal

Frontend sends files via FormData, receives structured JSON for:
- Resume → Question generation (via Groq LLM)
- Audio → Answer evaluation (via Groq LLM)  
- Video → Direct score storage (no LLM needed)

Backend remains LLM-agnostic; all AI reasoning handled in Next.js layer.

## Limitations & Trade-offs

- **Free tier constraints:** Required model size reduction (tiny vs base Whisper)
- **Frame sampling:** Analyzes 10% of frames (speed vs accuracy)
- **No state:** Each request independent (stateless architecture)

## License
MIT
**Built by Team Xtract** for PrepPal adaptive interview platform.
