import whisper
import redis
import json
import os
from pathlib import Path

# Initialize Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

# Initialize Whisper model
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
    
    while True:
        # Listen for new transcription requests
        _, request_data = redis_client.blpop('transcription_requests')
        request = json.loads(request_data)
        
        # Process the request
        result = process_transcription(request['audio_path'])
        
        # Store the result
        redis_client.set(
            f"transcription_result:{request['request_id']}",
            json.dumps(result)
        )

if __name__ == "__main__":
    main() 