from selenium import webdriver
import authenticate
import humblebundle
import logging
import sqlite3
import time


def main():
    # Build the logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s",
                                  "%Y/%m/%d %H:%M:%S")

    # File handler
    fh = logging.FileHandler("humblebundlesbot.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    # Stream handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    # Open and create the database if needed
    sql = sqlite3.connect("data.db")
    cur = sql.cursor()

    cur.execute("create table if not exists Bundles(Name TEXT NOT NULL, \
                URL TEXT NOT NULL UNIQUE, Date_Added TEXT NOT NULL)")
    cur.execute("create table if not exists Monthly(Name TEXT NOT NULL, \
                URL TEXT NOT NULL UNIQUE, Date_Added TEXT NOT NULL)")
    sql.commit()

    # Create a headless Chrome process
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-gpu")
    browser = webdriver.Chrome(chrome_options=options)
    browser.implicitly_wait(60)

    # Authenticate with Reddit API
    reddit = authenticate.auth()
    logger.info("Successfully authenticated as {}".format(reddit.user.me()))

    # Work loop
    # TODO: Close browser should we need to close prematurely
    while True:
        try:
            humblebundle.fetch_bundles(logger, sql, cur, browser, reddit)
            time.sleep(1)
            humblebundle.fetch_monthly(logger, sql, cur, browser, reddit)
        except Exception as e:
            logger.error(e)

        time.sleep(30)


if __name__ == "__main__":
    main()
