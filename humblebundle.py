from bs4 import BeautifulSoup
import time


def fetch_bundles(logger, sql, cur, browser, reddit):
    # Fetch HumbleBundle's main page
    # TODO: Handle potential errors
    browser.get("https://humblebundle.com")

    # Parse the rendered DOM
    soup = BeautifulSoup(browser.page_source, "html.parser")
    bundles = soup.find_all("div", {"class": ["bundle","navbar-tile"]})

    if len(bundles) > 0:
        for bundle in bundles:
            # Get the first link in the div
            link_tag = bundle.find("a")
            url = "https://www.humblebundle.com" + link_tag["href"]

            cur.execute("select * from Bundles where URL=?", [browser.current_url])
            if not cur.fetchone():
                title = bundle.find("span", {"class": "name"})

                logger.info("Found new bundle: {} -- {}".format(title, url))

                # TODO: This should try again if the API fails, not refetch the page
                try:
                    reddit.subreddit("humblebundles").submit(title, url=url)
                    timestamp = int(time.time())
                    cur.execute("insert into Bundles values(?,?,?)", [title, url, timestamp])
                    sql.commit()
                    time.sleep(5)
                except Exception as e:
                    logger.error(e)



def fetch_monthly(logger, sql, cur, reddit):
    headers = {"User-Agent": "reddit.com/u/humblebundlesbot"}

    date = datetime.now()
    month = date.strftime("%B")
    month_lower = month.lower()
    year = date.strftime("%Y")

    url = "https://www.humblebundle.com/monthly/p/" + month_lower + "_" + year + "_monthly"

    cur.execute("select * from Monthly where URL=?", [url])
    if not cur.fetchone():
        req = requests.get(url, headers=headers, stream=True)
        soup = BeautifulSoup(req.text, "html.parser")

        if soup.title.string != "Page not found":
            title = "{} {} Humble Monthly Bundle".format(month, year)
            # title = soup.find("meta", {"name": "title"})["content"]

            try:
                reddit.subreddit("humblebundles").submit(title, url=url)
                timestamp = int(time.time())
                cur.execute("insert into Bundles values(?,?,?)", [title, url, timestamp])
                sql.commit()
            except Exception as e:
                logger.error(e)
