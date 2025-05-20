import redis
import os
import uuid
import json

class RedisEnqueue():
    def __init__(self, host="redis", port=6379):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', host),
            port=int(os.getenv('REDIS_PORT', port)),
            decode_responses=True
        )

    def enqueue(self, asset: dict):
        try:
            # Generate request ID
            request_id = str(uuid.uuid4())

            # Create transcription request
            asset['request_id'] = request_id
            asset["audio_path"] = str(asset["audio_path"])
            # Send request to Whisper service
            self.redis_client.rpush('transcription_requests', json.dumps(asset))
        except Exception as e:
            print(e)

        return request_id

    def get_status(self, request_id):
        return self.redis_client.get(f"transcription_result:{request_id}")
