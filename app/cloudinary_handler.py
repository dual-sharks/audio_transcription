import cloudinary
import cloudinary.api
from dotenv import load_dotenv, find_dotenv
import os
from cloudinary.exceptions import Error as CloudinaryError
from app.asset import Asset
import requests
from pathlib import Path


def get_cloud_keys() -> tuple[str, str, str]:
    load_dotenv(find_dotenv())
    return (
        os.getenv("CLOUD_NAME"),
        os.getenv("CLOUD_API_KEY"),
        os.getenv("CLOUD_API_SECRET"),
    )


def set_cloud_config() -> None:
    cloud_name, cloud_api_key, cloud_api_secret = get_cloud_keys()
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=cloud_api_key,
        api_secret=cloud_api_secret,
        secure=True,
    )


def _raw_fetch(max_results: int):
    resp = cloudinary.api.resources(resource_type="video",
                                    max_results=max_results)
    list = []

    for resource in resp["resources"]:

        formatted_url = change_mp4_format(resource["secure_url"])

        list.append(Asset(public_id=resource["public_id"],
                          asset_id=resource["asset_id"],
                          secure_url=formatted_url))
    return list

def change_mp4_format(url: str) -> str:
    lower = url.lower()
    if lower.endswith(".mp4"):
        return url[:-4] + ".mp3"
    return url


def pull_cloud_vid_links(max_results: int = 10, _retry: bool = True):
    try:
        print("Raw Fetch")
        results = _raw_fetch(max_results)
        return results
    except Exception as e:
        set_cloud_config()
        if _retry:
            return pull_cloud_vid_links(max_results, _retry=False)

def download_mp3(asset: Asset):
    # 1. Fetch
    resp = requests.get(asset.secure_url)
    resp.raise_for_status()

    # 2. Ensure the directory exists
    audio_dir = Path("app/static/audio")
    audio_dir.mkdir(parents=True, exist_ok=True)

    # 3. Build a filename
    filename = f"{asset.asset_id}.mp3"
    file_path = audio_dir / filename

    print(f"Downloading {filename}")
    # 4. Write in binary mode
    with open(file_path, "wb") as f:
        f.write(resp.content)

    return file_path  # maybe return it so the caller knows where it went

