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

def listen_redis_queue():
    try:
        response = redis_client.dequeue()
        if response is not None:
            print(response)
            redis_client.set_status(
                response['request_id'],
                json.dumps({"status": "Processing transcription..."})
            )
            print(response)
            result = process_transcription(response['audio_path'])

            send_audio_details(response, result)
    except Exception as e:
        print(str(e))

def send_audio_details(audio_details: dict, result):
    # Store the result
    print(audio_details['request_id'])
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