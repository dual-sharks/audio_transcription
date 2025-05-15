import os
from pathlib import Path
from typing import List, Optional

import cloudinary
import cloudinary.api
from cloudinary.exceptions import Error as CloudinaryError
from dotenv import load_dotenv, find_dotenv
import requests

from app.asset import Asset


def get_cloud_keys() -> tuple[str, str, str]:
    """
    Loads Cloudinary credentials from a .env file and returns them as a tuple.

    Returns:
        Tuple of cloud_name, api_key, and api_secret.
    """
    load_dotenv(find_dotenv())
    return (
        os.getenv("CLOUD_NAME"),
        os.getenv("CLOUD_API_KEY"),
        os.getenv("CLOUD_API_SECRET"),
    )


def set_cloud_config() -> None:
    """
    Configures the Cloudinary client with environment variables.
    """
    cloud_name, cloud_api_key, cloud_api_secret = get_cloud_keys()
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=cloud_api_key,
        api_secret=cloud_api_secret,
        secure=True,
    )


def _raw_fetch(max_results: int) -> List[Asset]:
    """
    Fetches video resources from Cloudinary and converts their URLs to MP3 format.

    Args:
        max_results: Maximum number of video resources to fetch.

    Returns:
        A list of Asset objects with modified MP3 URLs.
    """
    resp = cloudinary.api.resources(resource_type="video", max_results=max_results)
    assets: List[Asset] = []

    for resource in resp["resources"]:
        formatted_url = change_mp4_format(resource["secure_url"])
        assets.append(
            Asset(
                public_id=resource["public_id"],
                asset_id=resource["asset_id"],
                secure_url=formatted_url,
                mp3_path=None,
                captions=None
            )
        )
    return assets


def change_mp4_format(url: str) -> str:
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


def pull_cloud_vid_links(max_results: int = 10, _retry: bool = True) -> Optional[List[Asset]]:
    """
    Attempts to fetch a list of video links from Cloudinary and format them as MP3 assets.

    Args:
        max_results: Number of results to retrieve.
        _retry: Whether to retry fetching after reinitializing config (used internally).

    Returns:
        A list of Asset objects or None on failure.
    """
    try:
        print("Raw Fetch")
        return _raw_fetch(max_results)
    except Exception as e:
        print(f"Error occurred: {e}. Retrying with config setup...")
        set_cloud_config()
        if _retry:
            return pull_cloud_vid_links(max_results, _retry=False)
        return None


def download_mp3(asset: Asset) -> Path:
    """
    Downloads an MP3 file from a secure URL and saves it to the local audio directory.

    Args:
        asset: The Asset object containing download metadata.

    Returns:
        The file path to the downloaded MP3 file.
    """
    # Fetch the file
    resp = requests.get(asset.secure_url)
    resp.raise_for_status()

    # Ensure the audio directory exists
    audio_dir = Path("app/static/audio")
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Define output file path
    filename = f"{asset.asset_id}.mp3"
    file_path = audio_dir / filename

    print(f"Downloading {filename}")
    # Write the file to disk
    with open(file_path, "wb") as f:
        f.write(resp.content)

    # link mp3 path to asset object
    asset.mp3_path = file_path

    return file_path