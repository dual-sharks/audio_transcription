from pydantic import BaseModel

class Asset(BaseModel):
    public_id: str
    asset_id: str
    secure_url: str
    mp3_path: str
    captions: str
