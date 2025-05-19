import whisper
import redis
import json
import os
from pathlib import Path
import torch
from app.services.redis_handler import Redis

# Initialize Whisper model
#DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base")



def process_transcription(audio_path: str) -> dict:
    """Process audio file with Whisper model"""

    try:
        result = model.transcribe(audio_path)
        return {
            "status": "completed",
            "text": result["text"],
            "segments": result["segments"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def main():
    print("Whisper service started. Waiting for transcription requests...")

    # Initialize Redis connection
    redis_client = Redis()

    while True:
        # Listen for new transcription requests
        request_data = redis_client.dequeue
        request = json.loads(request_data)
        
        # Process the request
        result = process_transcription(request['audio_path'])
        
        # Store the result
        redis_client.set(
            f"transcription_result:{request['request_id']}",
            json.dumps(result)
        )

        if result:
            print(result["text"])



if __name__ == "__main__":
    main() 