import logging
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

logger = logging.getLogger("RedditClient")
logger.propagate = False
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)

load_dotenv()

fh = logging.FileHandler("reddit_crawler.log")
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

class RedditClient:
    API_BASE = "https://oauth.reddit.com"
    TOKEN_URL = "https://www.reddit.com/api/v1/access_token"

    def __init__(self):
        self.headers = {
            "User-Agent": os.environ.get("REDDIT_USER_AGENT", "reddit-crawler"),
            "Authorization": f"Bearer {self.get_token()}"
        }

    def get_token(self):
        auth = requests.auth.HTTPBasicAuth(os.environ.get("REDDIT_CLIENT_ID"), os.environ.get("REDDIT_CLIENT_SECRET"))

        data = {
            "grant_type": "password",
            "username": os.environ.get("REDDIT_USERNAME"),
            "password": os.environ.get("REDDIT_PASSWORD"),
        }
        headers = {
            "User-Agent": os.environ.get("REDDIT_USER_AGENT", "reddit-crawler")
        }

        response = requests.post(self.TOKEN_URL, auth=auth, data=data, headers=headers)
        response.raise_for_status()
        token = response.json().get("access_token")
        return token
        
    def get_subreddit_posts(self, subreddit, limit=10):
        api_call = f"{self.API_BASE}/r/{subreddit}/new.json?limit={limit}"
        response = requests.get(api_call, headers=self.headers)
        if response.status_code == 200:
            logger.info(f"Successfully fetched posts from {subreddit}")
            return response.json().get("data", {}).get("children", [])
        else:
            logger.error(f"Failed to fetch posts from {subreddit}. Status code: {response.status_code}")
            return []

    def get_post_comments(self, subreddit, post_id, limit=10):
        api_call = f"{self.API_BASE}/r/{subreddit}/comments/{post_id}.json?limit={limit}"
        response = requests.get(api_call, headers=self.headers)
        if response.status_code == 200:
            logger.info(f"Successfully fetched comments for post {post_id} in {subreddit}")
            return response.json()[1].get("data", {}).get("children", [])
        else:
            logger.error(f"Failed to fetch comments for post {post_id} in {subreddit}. Status code: {response.status_code}")
            return []

if __name__ == "__main__":
    client = RedditClient()
    posts = client.get_subreddit_posts("climatechange", limit=5)
    print(f"Fetched {len(posts)} posts . . .")
    for post in posts:
        print(post["data"]["title"])
