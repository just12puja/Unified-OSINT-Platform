import os
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
if not APIFY_TOKEN:
    raise RuntimeError("APIFY_TOKEN missing in .env file")

ACTORS = {
    "instagram": "apify/instagram-scraper",
    "facebook": "apify/facebook-posts-scraper",
}
