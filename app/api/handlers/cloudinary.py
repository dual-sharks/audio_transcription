import cloudinary
import cloudinary.api
from cloudinary.exceptions import Error as CloudinaryError
from pathlib import Path
import os
from dotenv import load_dotenv
import requests
from typing import Optional, Dict

class CloudinaryHandler:
    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """
        Initialize CloudinaryHandler with credentials.
        
        Args:
            cloud_name: Cloudinary cloud name
            api_key: Cloudinary API key
            api_secret: Cloudinary API secret
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        self._configure_cloudinary()
        
    def _configure_cloudinary(self) -> None:
        """Configure Cloudinary with the provided credentials."""
        try:
            cloudinary.config(
                cloud_name=self.cloud_name,
                api_key=self.api_key,
                api_secret=self.api_secret,
                secure=True
            )
        except CloudinaryError as e:
            print(f"Error configuring Cloudinary: {e}")
            raise
    
    def _change_mp4_format(self, url: str) -> str:
        """
        Changes the file extension of a URL from .mp4 to .mp3 if applicable.

        Args:
            url: Original video URL.

        Returns:
            Modified URL pointing to an .mp3 file.
        """
        lower = url.lower()
        if lower.endswith(".mp4"):
            return url[:-4] + ".mp3"
        return url
    
    def pull_audio_details(self,
                           max_results: int = 500,
                           next_cursor: Optional[str] = None) -> Dict:
        """
        Fetches video resources from Cloudinary and converts their URLs to MP3 format.
        
        Args:
            max_results: Maximum number of video resources to fetch.
            
        Returns:
            A dictionary of Asset objects with modified MP3 URLs.
        """
        try:
            asset_dict = {}

            audio_dir = Path("static/audio")
            audio_dir.mkdir(parents=True, exist_ok=True)

            resp = cloudinary.api.resources(resource_type="video",
                                            max_results=max_results,
                                            tags=True,
                                            next_cursor=next_cursor)

            for resource in resp["resources"]:
                filename = f"{resource['asset_id']}.mp3"
                file_path = audio_dir / filename

                formatted_url = self._change_mp4_format(resource["secure_url"])

                asset_dict[resource["asset_id"]] = {
                    "public_id": resource["public_id"],
                    "asset_id": resource["asset_id"],
                    "secure_url": formatted_url,
                    "audio_path": file_path,
                }
                
            return {"assets": asset_dict,
                    "next_cursor": resp.get("next_cursor")}
        except CloudinaryError as e:
            print(f"Error fetching audio details: {e}")
            raise

    def pull_all_audio_details(self):
        all_assets: dict[str, dict] = {}
        next_cursor: str | None = None
        while True:
            page = self.pull_audio_details(next_cursor=next_cursor)
            all_assets.update(page["assets"])
            next_cursor = page.get("next_cursor")
            if not next_cursor:
                break
        return all_assets

    def download_audio(self, asset: Dict) -> bool:
        """
        Downloads an MP3 file from a secure URL and saves it to the local audio directory.

        Args:
            asset: The Asset object containing download metadata.

        Returns:
            True if download was successful, False otherwise.
        """
        try:
            resp = requests.get(asset["secure_url"])
            resp.raise_for_status()

            print(f"Downloading {asset['asset_id']}")
            with open(asset["audio_path"], "wb") as f:
                f.write(resp.content)

            asset["status"] = "Downloaded"
            return {
            "status": "Success",
            "message": "Audio downloaded successfully",
            "file_path": str(asset["audio_path"])
        }
        except (requests.RequestException, IOError) as e:
            asset["status"] = None
            print(f"Error downloading audio: {e}")
            return False

    def update_asset(self, contentful_details: dict) -> bool:
        if contentful_details["status"] == "completed":
            cloudinary.api.update(contentful_details["public_id"],
                                  context={"transcript": contentful_details["transcript"]})

    @classmethod
    def from_env(cls) -> 'CloudinaryHandler':
        """
        Create a CloudinaryHandler instance using environment variables.
        Automatically loads from .env file in project root.
        
        Returns:
            CloudinaryHandler instance configured with environment variables
        """
        project_root = Path(__file__).parent.parent.parent.parent
        env_path = project_root / '.env'
        
        if not load_dotenv(env_path):
            print(f"Warning: Could not find .env file at {env_path}")
        
        cloud_name = os.getenv("CLOUD_NAME")
        api_key = os.getenv("CLOUD_API_KEY")
        api_secret = os.getenv("CLOUD_API_SECRET")
        
        if not all([cloud_name, api_key, api_secret]):
            raise ValueError(
                "Missing required Cloudinary environment variables. "
                "Please ensure CLOUD_NAME, CLOUD_API_KEY, and CLOUD_API_SECRET "
                f"are set in your .env file at {env_path}"
            )
            
        return cls(cloud_name, api_key, api_secret)
