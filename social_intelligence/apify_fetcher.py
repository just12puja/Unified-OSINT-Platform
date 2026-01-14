from apify_client import ApifyClient
from config import APIFY_TOKEN, ACTORS

client = ApifyClient(APIFY_TOKEN)

def _safe_items(run):
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    return [item for item in items if isinstance(item, dict)]

def fetch_instagram(username, limit=5):
    run = client.actor(ACTORS["instagram"]).call(
        run_input={
            "directUrls": [f"https://www.instagram.com/{username}/"],
            "resultsType": "posts",
            "resultsLimit": limit
        }
    )
    return _safe_items(run)

def fetch_facebook(username, limit=5):
    run = client.actor(ACTORS["facebook"]).call(
        run_input={
            "startUrls": [{"url": f"https://www.facebook.com/{username}/"}],
            "resultsLimit": limit
        }
    )
    return _safe_items(run)
