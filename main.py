import json
import logging
import sqlite3
import time
import praw
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import humblebundle


def main():
    # Build the logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s",
                                  "%Y/%m/%d %H:%M:%S")

    # File handler
    file_handler = logging.FileHandler("humblebundlesbot.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Stream handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Open and create the database if needed
    sql = sqlite3.connect("data.db")
    cur = sql.cursor()

    cur.execute("create table if not exists bundles(name text not null, \
                url text not null unique, date_added text not null)")
    cur.execute("create table if not exists games(name text not null, \
                url text not null, date_added text not null)")
    cur.execute("create table if not exists monthly(name text not null, \
                url text not null unique, date_added text not null)")
    sql.commit()

    # Create a headless Firefox process
    options = webdriver.FirefoxOptions()
    options.headless = True

    browser = webdriver.Firefox(executable_path="./geckodriver", options=options)
    browser.implicitly_wait(30)
    browser.set_page_load_timeout(30)

    # Create our connection to Reddit
    with open("info.json", "r", encoding="UTF-8") as info_file:
        info_json = json.load(info_file)

    reddit = praw.Reddit(username="HumbleBundlesBot",
                         password=info_json["password"],
                         client_id=info_json["client_id"],
                         client_secret=info_json["client_secret"],
                         user_agent="HumbleBundlesBot")

    logger.info("Successfully authenticated as %s", reddit.user.me())

    # Work loop
    # TODO: Close browser should we need to close prematurely
    while True:
        try:
            humblebundle.fetch_bundles(logger, sql, cur, browser, reddit)
            time.sleep(1)
            humblebundle.fetch_free(logger, sql, cur, browser, reddit, info_json["ignored_games"])
            time.sleep(1)
            humblebundle.fetch_monthly(logger, sql, cur, browser, reddit)
        except WebDriverException as err:
            logger.error(err)

            # Closes the current browser and creates a new one
            # TODO: Does this cover all browser exceptions?
            browser.quit()
            browser = webdriver.Chrome(chrome_options=options)
            browser.implicitly_wait(60)
        # TODO: Degeneralize this exception
        except Exception as err:
            logger.error(err)

        time.sleep(60)


if __name__ == "__main__":
    main()
