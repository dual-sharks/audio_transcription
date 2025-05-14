from pydantic import BaseModel

class Asset(BaseModel):
    public_id: str
    asset_id: str
    secure_url: str
