from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import os

from typing import Optional
from app.api.handlers.cloudinary import CloudinaryHandler
from app.services.redis_handler import RedisEnqueue
from pathlib import Path

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
BASE_DIR = Path(__file__).resolve().parent          # …/app
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize Cloudinary handler
cloudinary_handler = CloudinaryHandler.from_env()

# Initialize Redis handler
redis_client = RedisEnqueue('localhost')


@app.get("/")
async def root():
    return {"status": "healthy", "message": "Audio Transcription API is running"}


@app.get("/cloudinary/videos")
async def list_videos():
    """List all available videos from Cloudinary."""
    try:
        assets = cloudinary_handler.pull_audio_details()

        if not assets:
            raise HTTPException(status_code=404, detail="No audio files found")
        return {
            "status": "success",
            "message": "URLs pulled successfully",
            "assets": assets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cloudinary/videos/all")
async def list_all_videos():
    try:
        assets = cloudinary_handler.pull_all_audio_details()
        if not assets:
            raise HTTPException(status_code=404, detail="No audio files found")
        return {"status": "success",
                "message": "All URLs pulled successfully",
                "assets": assets["assets"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cloudinary/videos/{asset_id}/download")
async def download_audio(asset_id: str):
    """Download a specific video by its asset ID."""
    try:
        # First get all assets
        assets = cloudinary_handler.pull_audio_details()
        if asset_id not in assets:
            raise HTTPException(status_code=404, detail="Asset not found")

        asset = assets[asset_id]
        if not asset["audio_path"].exists():
            success = cloudinary_handler.download_audio(asset)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to download audio")

        return {
            "status": "success",
            "message": "Audio downloaded successfully",
            "asset": asset
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe/{asset_id}")
async def transcribe_audio(asset_id: str, background_tasks: BackgroundTasks):
    """
    Transcribe a specific audio file by its asset ID.
    For now, just verifies the file exists.
    """
    try:
        # First get all assets
        assets = cloudinary_handler.pull_audio_details()
        if asset_id not in assets:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        asset = assets[asset_id]
        if not asset["audio_path"].exists():
            raise HTTPException(
                status_code=400, 
                detail="Audio file not downloaded. Please download first."
            )

        request_id = redis_client.enqueue(asset)

        message = {
            "status": "queued",
            "message": "asset is queued for transcription",
            "asset": asset
        }

        redis_client.set_status(request_id, json.dumps(message))

        return message
    except HTTPException:
        raise
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
                "status": "Not Processing",
                "message": "Transcription not in progress, nothing found"
            }

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dequeue/transcription")
async def get_next_transcription():
    try:
        result = redis_client.dequeue()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result


@app.post("/cloudinary/upload{asset_id}")
async def upload_text(asset_id: str):
    #cloudinary_handler
    return {"status": "success", "message": "Upload functionality pending"}


@app.get("/contentfuloutput/{asset_id}")
async def get_contentful_output(asset_id: str):
    try:
        response = json.loads(redis_client.get_status(asset_id))
        asset = response["asset"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if response["status"] == "success" and response["text"]:
        return {"status": response["status"],
                "asset_id": asset["asset_id"],
                "public_id": asset["public_id"],
                "cloudinary_url": asset["url"],
                "transcript": asset["text"]}
    else:
        return {"status": "error",
                "message": "contentful output not stored in redis"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)