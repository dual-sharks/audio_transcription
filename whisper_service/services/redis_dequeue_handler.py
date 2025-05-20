import redis
import os
import uuid
import json

class RedisDequeue():
    def __init__(self, host="redis", port=6379):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', host),
            port=int(os.getenv('REDIS_PORT', port)),
            decode_responses=True
        )

    def dequeue(self):
        try:
            response = self.redis_client.blpop('transcription_requests')[1]
            json_response = json.loads(response)
        except Exception as e:
            print(e)
        if not json_response["request_id"]:
            return None
        return json_response

    def get_status(self, request_id):
        return self.redis_client.get(f"transcription_result:{request_id}")
