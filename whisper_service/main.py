import whisper
import redis
import json
import os
from pathlib import Path
import torch
from services.redis_dequeue_handler import RedisDequeue
import requests

# Initialize Whisper model
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=DEVICE)

# Initialize Redis connection
redis_client = RedisDequeue("localhost")


def process_transcription(audio_details: dict) -> dict:
    """Process audio file with Whisper model"""

    try:
        result = model.transcribe(audio_details["audio_path"])

        return {
            "status": "completed",
            "asset_id": audio_details["asset_id"],
            "public_id": audio_details["public_id"],
            "cloudinary_url": audio_details["secure_url"],
            "transcript": result["text"],
            "segments": result["segments"],
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def listen_redis_queue():
    try:
        response = redis_client.dequeue()
        if response is not None:
            redis_client.set_status(
                response['request_id'],
                json.dumps({"status": "processing",
                            "message": "Processing transcription",
                            "asset": response})
            )

            result = process_transcription(response)
            set_response_details(response, result)
    except Exception as e:
        print(str(e))

def set_response_details(audio_details: dict, result):
    if result["status"] == "completed":
        # Store the result
        redis_client.set_status(
            audio_details['asset_id'],
            json.dumps(result)
        )

        result["message"] = f"Audio details stored at {audio_details['asset_id']} in redis"


    redis_client.set_status(
        audio_details['request_id'],
        json.dumps(result)
    )
def main():
    print("Whisper service started. Waiting for transcription requests...")



    while True:
        listen_redis_queue()


if __name__ == "__main__":
    main() 