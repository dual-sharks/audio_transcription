import cloudinary
import cloudinary.api
from dotenv import load_dotenv, find_dotenv
import os
from cloudinary.exceptions import Error as CloudinaryError
from app.asset import Asset


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
    return [
        Asset(
            public_id=r["public_id"],
            asset_id=r["asset_id"],
            url=r["url"],
            secure_url=r["secure_url"],
        )
        for r in resp["resources"]
    ]


def pull_cloudinary_videos(max_results: int = 10, _retry: bool = True):

    try:
        results = _raw_fetch(max_results)
        return results
    except Exception as e:
        set_cloud_config()
        if _retry:
            return pull_cloudinary_videos(max_results, _retry=False)

