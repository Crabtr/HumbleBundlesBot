import json
import praw


def auth():
    # Open and parse the client information
    with open("info.json", "r", encoding="UTF-8") as info_file:
        info_json = json.load(info_file)

    # Create our connection to Reddit
    reddit = praw.Reddit(username="HumbleBundlesBot",
                         password=info_json["password"],
                         client_id=info_json["client_id"],
                         client_secret=info_json["client_secret"],
                         user_agent="HumbleBundlesBot")

    return reddit
