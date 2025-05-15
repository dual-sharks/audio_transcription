import redis
import os
from asset import Asset
import uuid
import json

class Redis():
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )

    def enqueue(self, asset: Asset):
        try:
            # Generate request ID
            request_id = str(uuid.uuid4())

            # Create transcription request
            request = {
                "request_id": request_id,
                "audio_path": asset.mp3_path,
                "asset_id": asset.asset_id,
            }

            # Send request to Whisper service
            self.redis_client.rpush('transcription_requests', json.dumps(request))
        except Exception as e:
            print(e)

            return request_id

    def dequeue(self):
        try:
            response = self.redis_client.lpop('transcription_requests')
        except Exception as e:
            print(e)
        if response is None:
            return None
        return response

    def get_status(self, request_id):
        return self.redis_client.get(f"transcription_result:{request_id}")
