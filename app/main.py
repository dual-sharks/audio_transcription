from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import os
from pathlib import Path
from typing import Optional
import app.cloudinary_handler as cloudinary_handler
from app.redis_handler import Redis



app = FastAPI(title="Audio Transcription API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize Redis connection
redis_client = Redis()

# Store Asset Dicts
assets_dict = {}

@app.get("/")
async def root():
    return {"status": "healthy", "message": "Audio Transcription API is running"}

@app.get("/cloudinary/videos/refresh")
async def pull_videos():
    try:
        assets = cloudinary_handler.pull_audio_details()
        if not assets:
            raise HTTPException(status_code=404, detail="Video file(s) not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"assets": assets}

@app.post("/cloudinary/videos/download/{assfet}")
async def download_audio(asset: dict):
    if not asset["audio_path"].exists():
        cloudinary_handler.download_audio(asset)

    return {"status": "processing"}

@app.post("/transcribe/{asset}")
async def transcribe_audio(asset: dict, background_tasks: BackgroundTasks):
    try:
        # Check if file exists
        if not asset["audio_path"].exists():
            raise HTTPException(status_code=404, detail="Audio file not found")

        request_id = redis_client.enqueue(asset)

        return {
            "request_id": request_id,
            "status": "processing",
            "message": "Transcription request received"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transcription/{request_id}")
async def get_transcription_status(request_id: str):
    try:
        # Check if result exists
        result = redis_client.get_status(request_id)
        if result is None:
            return {
                "request_id": request_id,
                "status": "processing",
                "message": "Transcription in progress"
            }
        
        return json.loads(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 