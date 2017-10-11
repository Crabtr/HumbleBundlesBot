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
    sql.commit()

    # Authenticate with Reddit API
    reddit = authenticate.auth()
    logger.info("Successfully authenticated as {}".format(reddit.user.me()))

    # Work loop
    while True:
        try:
            humblebundle.fetch_bundles(logger, sql, cur, reddit)
            humblebundle.fetch_monthly(logger, sql, cur, reddit)
        except Exception as e:
            logger.error(e)

        time.sleep(30)


if __name__ == "__main__":
    main()
