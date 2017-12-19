import logging
import sqlite3
import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import authenticate
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
    logger.info("Successfully authenticated as %s", reddit.user.me())

    # Work loop
    # TODO: Close browser should we need to close prematurely
    while True:
        try:
            humblebundle.fetch_bundles(logger, sql, cur, browser, reddit)
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

        time.sleep(30)


if __name__ == "__main__":
    main()
