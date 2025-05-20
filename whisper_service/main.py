import whisper
import redis
import json
import os
from pathlib import Path
import torch
from services.redis_dequeue_handler import RedisDequeue

# Initialize Whisper model
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=DEVICE)



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
    redis_client = RedisDequeue("localhost")

    while True:
        # Listen for new transcription requests
        request_data = redis_client.dequeue()
        if request_data:
            # Process the request
            redis_client.set_status(
                request_data['request_id'],
                json.dumps({"status": "Processing transcription..."})
            )

            result = process_transcription(request_data['audio_path'])

        
            # Store the result
            redis_client.set_status(
                request_data['request_id'],
                json.dumps(result)
            )

if __name__ == "__main__":
    main() 