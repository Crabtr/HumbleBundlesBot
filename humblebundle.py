from datetime import datetime
import time
from bs4 import BeautifulSoup
from furl import furl


def fetch_bundles(logger, sql, cur, browser, reddit):
    # Fetch HumbleBundle's main page
    # TODO: Handle potential errors
    browser.get("https://humblebundle.com")

    # Parse the rendered DOM
    soup = BeautifulSoup(browser.page_source, "html.parser")

    if soup is not None:
        dropdown = soup.find("div", {"class": "bundle-dropdown-content"})
        bundles = dropdown.select("a.bundle.navbar-tile")

        for bundle in bundles:
            # Remove query parameters from the URL
            link = furl("https://www.humblebundle.com" + bundle["href"])
            link.remove(link.args)

            cur.execute("select * from bundles where url=?", [link.url])
            if not cur.fetchone():
                title = bundle.find("span", {"class": "name"})
                title = title.text

                logger.info("Found new bundle: {} -- {}".format(title, link.url))

                # TODO: This should try again if the API fails, not refetch the page
                try:
                    reddit.subreddit("humblebundles").submit(title, url=link.url)
                    timestamp = int(time.time())
                    cur.execute("insert into bundles values(?,?,?)", [title, link.url, timestamp])
                    sql.commit()
                    time.sleep(5)
                # TODO: Degeneralize this exception
                except Exception as err:
                    logger.error(err)


def fetch_free(logger, sql, cur, browser, reddit, ignored_games):
    # Fetch HumbleBundle's store page with the games on sale
    browser.get("https://www.humblebundle.com/store/search?sort=discount&filter=onsale")

    # Parse the rendered DOM
    soup = BeautifulSoup(browser.page_source, "html.parser")

    if soup is not None:
        games = soup.select("div.entity.on-sale")

        for game in games:
            discount_percentage = game.select_one("span.discount-percentage")

            if discount_percentage.text == "-100%":
                title = game.select_one("span.entity-title").text

                if title not in ignored_games:
                    link_tag = game.select_one("a.entity-link")

                    url = furl("https://www.humblebundle.com" + link_tag["href"])
                    url.remove(url.args)

                    # Ensure it's been 14 days since the game was last posted
                    # TODO: Should this be pushed to a month?
                    timestamp = int(time.time())

                    cur.execute("select * from games where url=? and (?-date_added) >= 1209600", [url.url, timestamp])
                    if not cur.fetchone():
                        logger.info("Found new free game: {} -- {}".format(title, url.url))

                        submission_title = title + " is available for free!"

                        # TODO: This should try again on failure
                        try:
                            reddit.subreddit("humblebundles").submit(submission_title, url.url)
                            cur.execute("insert into games values(?,?,?)", [title, url.url, timestamp])
                            sql.commit()
                            time.sleep(5)
                        # TODO: Degeneralize this exception
                        except Exception as err:
                            logger.error(err)


def fetch_monthly(logger, sql, cur, browser, reddit):
    # Build the URL for this month's bundle
    date = datetime.now()
    month = date.strftime("%B")
    month_lower = month.lower()
    year = date.strftime("%Y")

    url = "https://www.humblebundle.com/monthly/p/" + month_lower + "_" + year + "_monthly"

    cur.execute("select * from monthly where url=?", [url])
    if not cur.fetchone():
        # Fetch the url
        # TODO: Handle potential errors
        browser.get(url)
        soup = BeautifulSoup(browser.page_source, "html.parser")

        if soup.title.string != "Page not found":
            title = "{} {} Humble Monthly Bundle".format(month, year)

            logger.info("Found new monthly bundle: {} -- {}".format(title, url))

            # TODO: This should try again if the API fails, not refetch the page
            try:
                reddit.subreddit("humblebundles").submit(title, url=url)
                timestamp = int(time.time())
                cur.execute("insert into monthly values(?,?,?)", [title, url, timestamp])
                sql.commit()
            # TODO: Degeneralize this exception
            except Exception as err:
                logger.error(err)
