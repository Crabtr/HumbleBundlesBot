from datetime import datetime
import time
from bs4 import BeautifulSoup


def fetch_bundles(logger, sql, cur, browser, reddit):
    # Fetch HumbleBundle's main page
    # TODO: Handle potential errors
    browser.get("https://humblebundle.com")

    # Parse the rendered DOM
    soup = BeautifulSoup(browser.page_source, "html.parser")

    if soup is not None:
        dropdown = soup.find("div", {"class": "bundle-dropdown-content"})
        bundles = dropdown.find_all("div", {"class": ["bundle", "navbar-tile"]})

        for bundle in bundles:
            # Get the first link in the div
            link_tag = bundle.find("a")
            link_path = ""

            # Remove query parameters from the URL
            for char in link_tag["href"]:
                if char != "?":
                    link_path += char
                else:
                    break

            link = "https://www.humblebundle.com" + link_path

            cur.execute("select * from Bundles where URL=?", [link])
            if not cur.fetchone():
                title = bundle.find("span", {"class": "name"})
                title = title.text

                logger.info("Found new bundle: {} -- {}".format(title, link))

                # TODO: This should try again if the API fails, not refetch the page
                try:
                    reddit.subreddit("humblebundles").submit(title, url=link)
                    timestamp = int(time.time())
                    cur.execute("insert into Bundles values(?,?,?)", [title, link, timestamp])
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

    cur.execute("select * from Monthly where URL=?", [url])
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
                cur.execute("insert into Monthly values(?,?,?)", [title, url, timestamp])
                sql.commit()
            # TODO: Degeneralize this exception
            except Exception as err:
                logger.error(err)
