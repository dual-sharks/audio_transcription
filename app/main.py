from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import os
from pathlib import Path
from typing import Optional
from app.api.handlers.cloudinary import CloudinaryHandler

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

# Initialize Cloudinary handler
cloudinary_handler = CloudinaryHandler.from_env()

@app.get("/")
async def root():
    return {"status": "healthy", "message": "Audio Transcription API is running"}

@app.get("/cloudinary/videos")
async def list_videos():
    """List all available videos from Cloudinary."""
    try:
        assets = cloudinary_handler.pull_audio_details()
        if not assets:
            raise HTTPException(status_code=404, detail="No video files found")
        return {"assets": assets}
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
            "file_path": str(asset["audio_path"])
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
        
        # TODO: Implement actual transcription
        return {
            "status": "not_implemented",
            "message": "Transcription functionality coming soon",
            "asset_id": asset_id,
            "file_path": str(asset["audio_path"])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 