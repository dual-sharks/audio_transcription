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

    def dequeue(self):
        try:
            response = self.redis_client.blpop('transcription_requests')
        except Exception as e:
            print(e)

        return response

    def get_status(self, request_id):

        #TODO: Implement getting transcript in these formats:
        """
        Contentful Sync Output
         {
            "audio_id": "abc123",
            "cloudinary_url": "https://res.cloudinary.com/cloud-name/audio/example.mp3",
            "transcript": "Full transcription text here"
        }

        Training Dataset Output
        {
            "audio_id": "abc123",
            "transcript": "Full transcription text here",
            “description”: “Full description text here”,
            "tags": ["Romance", "Fantasy", "Love"]
        }
        """

        return self.redis_client.get(f"transcription_result:{request_id}")
