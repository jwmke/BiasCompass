import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Mention listener
class MentionListener(tweepy.StreamListener):
    def on_status(self, tweet):
        # Ignore retweets
        if tweet.retweeted or tweet.in_reply_to_status_id is not None:
            return

        # Reply to mentions
        username = tweet.user.screen_name
        tweet_id = tweet.id_str
        mention_text = tweet.text
        reply_text = f"Testing. Username: @{username}, Article: {mention_text}"

        api.update_status(
            status=reply_text,
            in_reply_to_status_id=tweet_id,
            auto_populate_reply_metadata=True,
        )

    def on_error(self, status_code):
        if status_code == 420:
            return False

# Create a stream listener
listener = MentionListener()
stream = tweepy.Stream(auth=api.auth, listener=listener)

# Start streaming for mentions
stream.filter(track=["@BiasCompass"])