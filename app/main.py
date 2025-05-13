from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import redis
import json
import os
import uuid
from pathlib import Path
from typing import Optional
from app import cloudinary_handler

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
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

@app.get("/")
async def root():
    return {"status": "healthy", "message": "Audio Transcription API is running"}

@app.get("/cloudinary/videos")
async def pull_cloudinary_videos():
    try:
        videos = cloudinary_handler.get_cloudinary_videos()
    except Exception as e:
        raise HTTPException()

    return {"videos": videos}

@app.post("/transcribe/{filename}")
async def transcribe_audio(filename: str, background_tasks: BackgroundTasks):
    try:
        # Check if file exists
        audio_path = Path("app/static/audio") / filename
        if not audio_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Create transcription request
        request = {
            "request_id": request_id,
            "audio_path": str(audio_path)
        }
        
        # Send request to Whisper service
        redis_client.rpush('transcription_requests', json.dumps(request))
        
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
        result = redis_client.get(f"transcription_result:{request_id}")
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