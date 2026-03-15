from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import resume, video, audio, evaluation
import os

load_dotenv()

app = FastAPI(title="Interview AI Backend")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(resume.router)
app.include_router(video.router)
app.include_router(audio.router)
app.include_router(evaluation.router)
@app.get("/")
def health_check():
    return {"status": "Interview AI Backend Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
