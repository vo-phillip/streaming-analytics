import praw
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD, REDDIT_USER_AGENT, REDIS_HOST, REDIS_PORT
import redis
import json
import time

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    user_agent=REDDIT_USER_AGENT
)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

while True:
    posts = reddit.subreddit("leagueoflegends").new(limit=100)
    for post in posts:
        if r.sismember("seen_post_ids", post.id):
            continue
        print(f"Subreddit Title: {post.title}, Score: {post.score}")
        post_data = json.dumps({"title": post.title, "score": post.score, "id": post.id, "created_utc": post.created_utc})
        r.rpush("reddit_posts", post_data)
        r.sadd("seen_post_ids", post.id)
    time.sleep(60)

