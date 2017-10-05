import json
import praw


def auth():
    # Open and parse the client information
    with open("info.json", "r", encoding="UTF-8") as infoFile:
        infoJSON = json.load(infoFile)

    # Create our connection to Reddit
    reddit = praw.Reddit(username="HumbleBundlesBot",
                         password=infoJSON["password"],
                         client_id=infoJSON["client_id"],
                         client_secret=infoJSON["client_secret"],
                         user_agent="HumbleBundlesBot")

    return reddit
