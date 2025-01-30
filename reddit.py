import requests
import time
from datetime import datetime, timedelta

def fetch_today_reddit_posts(subreddit, keyword=None, limit=100):
    # Calculate UNIX timestamp for the start of today (midnight)
    today_midnight = int(datetime.combine(datetime.today(), datetime.min.time()).timestamp())
    
    url = f'https://www.reddit.com/r/{subreddit}/new.json'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    all_posts = []
    after = None
    fetched_posts = 0

    while fetched_posts < limit:
        params = {'limit': 100}  # Fetch 100 posts per request
        if after:
            params['after'] = after
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error: Failed to retrieve the page. Status code: {response.status_code}")
            return []

        data = response.json()
        posts = data.get('data', {}).get('children', [])
        
        if not posts:
            break
        
        for post in posts:
            post_info = post['data']
            created_utc = post_info.get('created_utc', 0)
            
            # Only process posts created after today's midnight
            if created_utc >= today_midnight:
                title = post_info.get('title', 'No title')
                link = f"https://reddit.com{post_info.get('permalink', '')}"
                
                # If keyword filtering is enabled
                if keyword is None or keyword.lower() in title.lower():
                    all_posts.append({'title': title, 'link': link})
                    fetched_posts += 1
            
            if fetched_posts >= limit:
                break

        after = data.get('data', {}).get('after', None)
        
        if not after:
            break

    return all_posts

# Example usage
if __name__ == "__main__":
    subreddit = 'climatechange'
    
    # Fetch posts starting from today
    posts = fetch_today_reddit_posts(subreddit, limit=100)
    print(f"Total posts found today: {len(posts)}")
    for i, post in enumerate(posts, 1):
        print(f"Post {i}:")
        print(f"Title: {post['title']}")
        print(f"Link: {post['link']}\n")
    
    # Fetch posts from today containing the keyword "climate change"
    keyword_posts = fetch_today_reddit_posts(subreddit, keyword='climate change', limit=100)
    print(f"\nTotal posts today with keyword 'climate change': {len(keyword_posts)}")
    for i, post in enumerate(keyword_posts, 1):
        print(f"Post {i}:")
        print(f"Title: {post['title']}")
        print(f"Link: {post['link']}\n")
