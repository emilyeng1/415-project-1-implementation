import logging
import time
import datetime
from pyfaktory import Client, Producer, Consumer, Job
from reddit_client import RedditClient
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import Json
from psycopg2.extensions import register_adapter
import requests

logger = logging.getLogger("RedditCrawler")
logger.propagate = False
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)

load_dotenv()

FAKTORY_SERVER_URL = os.environ.get("FAKTORY_SERVER_URL")
DATABASE_URL = os.environ.get("DATABASE_URL")

register_adapter(dict, Json)

fh = logging.FileHandler("reddit_crawler.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
                
def get_toxicity_score(comment):
    API_URL = "https://api.moderatehatespeech.com/api/v1/moderate/"

    data = {
        "token": os.environ.get("MODERATE_HATE_SPEECH_API_KEY"),
        "text": comment
    }
    try:
        response = requests.post(API_URL, json=data).json()
        return response["class"]
    except Exception as e:
        logger.error(f"Failed to fetch toxicity score: {e}")
        return None
    except ValueError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return None

def store_post(subreddit, post):
    conn = psycopg2.connect(dsn=DATABASE_URL)
    cur = conn.cursor()

    post_id = post["data"]["id"]
    post_title = post["data"]["title"]
    post_data = post["data"]
    toxicity_score = post_data.get("toxicity_score")

    logger.debug(f"Storing post with Post ID: {post_id}, Toxicity: {toxicity_score}")

    cur.execute("SELECT 1 FROM posts WHERE subreddit = %s AND post_id = %s", (subreddit, post_id),)
    if cur.fetchone():
        logger.info(f"Post already exists: {subreddit}/{post_id}")
    else:
        query = "INSERT INTO posts (subreddit, post_id, post_title, data, toxicity_score) VALUES (%s, %s, %s, %s, %s) RETURNING post_id"
        cur.execute(query, (subreddit, post_id, post_title, post_data, toxicity_score))
        conn.commit()
        db_id = cur.fetchone()[0]
        logger.info(f"Inserted DB id: {db_id} for post {subreddit}/{post_id} with toxicity: {toxicity_score}")

    cur.close()
    conn.close()

def store_comment(post_id, comment):
    conn = psycopg2.connect(dsn=DATABASE_URL)
    cur = conn.cursor()

    comment_id = comment["data"]["id"]
    comment_body = comment["data"].get("body")
    toxicity_score = comment["data"].get("toxicity")

    if comment_body in ["[deleted]", "[removed]", None]:
        logger.info(f"Skipping deleted/removed comment: {comment}")
        return

    logger.debug(f"Storing comment with ID: {comment_id}, Post ID: {post_id}, Toxicity: {toxicity_score}")

    cur.execute("SELECT 1 FROM comments WHERE post_id = %s AND comment_id = %s", (post_id, comment_id),)
    if cur.fetchone():
        logger.info(f"Comment already exists: {post_id}/{comment_id}")
    else:
        query = "INSERT INTO comments (post_id, comment_id, comment_body, toxicity_score) VALUES (%s, %s, %s, %s) RETURNING comment_id"
        cur.execute(query, (post_id, comment_id, comment_body, toxicity_score))
        conn.commit()
        db_id = cur.fetchone()[0]
        logger.info(f"Inserted DB id: {db_id} for comment {post_id}/{comment_id}")
    
    cur.close()
    conn.close()

def crawl_subreddit(subreddit, previous_post_ids=[]):
    reddit_client = RedditClient()
    posts = reddit_client.get_subreddit_posts(subreddit, limit=10)
    for post in posts:
        post_id = post["data"]["id"]
        post_title = post["data"]["title"]
        post_body = post["data"].get("selftext", "")
        full_text = f"{post_title}\n{post_body}"

        toxicity_score = get_toxicity_score(full_text)
        post["data"]["toxicity_score"] = toxicity_score
        store_post(subreddit, post)
        
        comments = reddit_client.get_post_comments(subreddit, post_id, limit=10)
        for comment in comments:
            comment_body = comment["data"].get("body", "")

            if comment_body not in ["[deleted]", "[removed]", None]:
                comment_toxicity = get_toxicity_score(comment_body)
                comment["data"]["toxicity"] = comment_toxicity
            
            store_comment(post_id, comment)

def produce_jobs(subreddits):
    with Client(faktory_url=FAKTORY_SERVER_URL, role="producer") as client:
        producer = Producer(client=client)
        for subreddit in subreddits:
            job = Job(jobtype="crawl-subreddit", args=(subreddit,), queue="crawl-subreddit")
            producer.push(job)
            logger.info(f"Pushed job for subreddit: {subreddit}")


if __name__ == "__main__":
    import sys
    subreddits = ["climatechange", "climateactionplan", "EnvironmentalPolitics", "conspiracy"]
    if "produce" in sys.argv:
        logger.info("Starting continuous job production . . .")

        try:
            while True:
                produce_jobs(subreddits)
                time.sleep(300)
        except Exception as e:
            logger.error(f"Error in producer loop: {e}")
        except KeyboardInterrupt:
            logger.info("Producer stopped manually.")
    
    elif "consume" in sys.argv:
        logger.info("Starting continuous Faktory consumer...")

        with Client(faktory_url=FAKTORY_SERVER_URL, role="consumer") as client:
            consumer = Consumer(
                client=client,
                queues=["crawl-subreddit"],
                concurrency=5
            )
            consumer.register("crawl-subreddit", crawl_subreddit)

            try:
                consumer.run() 
            except KeyboardInterrupt:
                logger.info("Consumer stopped manually.")
    else:
        print("Usage: python reddit_crawler.py [produce|consume]")
