import cloudinary.api
from app.video_details import Asset

def pull_videos_cloudinary(max_results=10):
    try:
        response = cloudinary.api.resources(resource_type='video',
                                            max_results=max_results)
    except Exception as e:
        print(e)
    asset_list = []
    for asset in response['resources']:
        asset_list.append(Asset(public_id=asset['public_id'],
                                asset_id=asset['asset'],
                                url=asset['url'],
                                secure_url=asset['secure_url'],))

    return asset_list