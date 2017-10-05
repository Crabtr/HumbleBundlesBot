from bs4 import BeautifulSoup
import requests
import time


def fetch_bundles(logger, sql, cur, reddit):
    headers = {"User-Agent": "reddit.com/u/humblebundlesbot"}

    urls = [
        "https://www.humblebundle.com",
        "https://www.humblebundle.com/mobile",
        "https://www.humblebundle.com/software",
        "https://www.humblebundle.com/books"
    ]

    for url in urls:
        req = requests.get(url, headers=headers, allow_redirects=True, stream=True)
        soup = BeautifulSoup(req.text, "html.parser")

        page_handler(logger, sql, cur, reddit, soup)

        time.sleep(5)

        subtab_container = soup.find("div", {"id": "subtab-container"})
        if subtab_container:
            buttons = subtab_container.find_all("a", {"class": "subtab-button"})

            if buttons:
                for button in buttons:
                    if button["href"] != "#heading-logo":
                        button_url = "https://humblebundle.com" + button["href"]

                        req = requests.get(button_url, headers=headers, allow_redirects=True, stream=True)
                        soup = BeautifulSoup(req.text, "html.parser")

                        page_handler(logger, sql, cur, reddit, soup)

                        time.sleep(5)

        time.sleep(5)


def page_handler(logger, sql, cur, reddit, soup):
    link = soup.find("link", {"rel": "canonical"})["href"]
    title = soup.find("meta", {"name": "title"})["content"]

    cur.execute("select * from Bundles where Link=?", [link])
    if not cur.fetchone():
        logger.info("Found new bundle: {} -- {}".format(title, link))

        try:
            reddit.subreddit("narwhal_testing").submit(title, url=link)
            timestamp = int(time.time())
            cur.execute("insert into Bundles values(?,?,?)", [title, link, timestamp])
            sql.commit()
        except Exception as e:
            logger.error(e)
