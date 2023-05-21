from requests_oauthlib import OAuth1Session
import os
import json
from dotenv import load_dotenv

load_dotenv()

# consumer_key = os.environ.get("CONSUMER_KEY")
# consumer_secret = os.environ.get("CONSUMER_SECRET")

# # Get request token
# request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
# oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

# try:
#     fetch_response = oauth.fetch_request_token(request_token_url)
# except ValueError:
#     print(
#         "There may have been an issue with the consumer_key or consumer_secret you entered."
#     )

# resource_owner_key = fetch_response.get("oauth_token")
# resource_owner_secret = fetch_response.get("oauth_token_secret")
# print("Got OAuth token: %s" % resource_owner_key)

# # Get authorization
# base_authorization_url = "https://api.twitter.com/oauth/authorize"
# authorization_url = oauth.authorization_url(base_authorization_url)
# print("Please go here and authorize: %s" % authorization_url)
# verifier = input("Paste the PIN here: ")

# # Get the access token
# access_token_url = "https://api.twitter.com/oauth/access_token"
# oauth = OAuth1Session(
#     consumer_key,
#     client_secret=consumer_secret,
#     resource_owner_key=resource_owner_key,
#     resource_owner_secret=resource_owner_secret,
#     verifier=verifier,
# )
# oauth_tokens = oauth.fetch_access_token(access_token_url)

# access_token = oauth_tokens["oauth_token"]
# access_token_secret = oauth_tokens["oauth_token_secret"]

# print(f"access_token: {access_token}")
# print(f"access_token_secret: {access_token_secret}")

oauth = OAuth1Session(
        os.environ.get("CONSUMER_KEY"), 
        client_secret=os.environ.get("CONSUMER_SECRET"), 
        resource_owner_key=os.environ.get("ACCESS_TOKEN"), 
        resource_owner_secret=os.environ.get("ACCESS_SECRET"),
    )
payload = {"text": "Hello World!"}

# Making the request
response = oauth.post(
    "https://api.twitter.com/2/tweets",
     json=payload
)

# TODO: 
# 1. Test replying to a mention with the same text the user sends
# 2. Get tweet id of all mentions
# 3. Per mention: 
#   1. Get article link (do some validation)
#   2. Run article through compass_v2 logic
#   3. Reply to tweet via id with evaluation

print(response)