"""RPGnet Scraper.

Usage:
    scraper.py USERNAME PASSWORD
    scraper.py [options]

Options:
    -h --help       Show this help text."""

import sqlite3
from docopt import docopt
from robobrowser import RoboBrowser
import re
from dateutil.parser import parse
from datetime import datetime
from time import sleep


# SETUP
forum = "http://forum.rpg.net/"
searchbase = "search.php?do=finduser&userid={}&contenttype=vBForum_Post&showposts=1&searchdate={}&beforeafter=before"


b = RoboBrowser(user_agent="Firefox", history=False)
now = datetime.now()


conn = sqlite3.connect("post-archive.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
conn.execute("""CREATE TABLE IF NOT EXISTs posts (id integer primary key, url text, date timestamp, category text, title text, message text)""")
conn.commit()

c = conn.cursor()

# LOGIN


def login(username, password):
    """
    Log into rpg.net using username/password and return user id.

    :param username: Your rpg.net username as String.
    :param password: Your rpg.net password as String.
    :return: String of the numerical rpg.net user id.
    """
    b.open(forum + "login.php?do=login")

    print("Trying to login")
    loginform = b.get_form()

    loginform["vb_login_username"] = username
    loginform["vb_login_password"] = password

    loginform.serialize()

    b.submit_form(loginform)

    assert b.response.status_code == 200

    print("Logged in.")

    # get user id
    b.open("http://forum.rpg.net")
    link = b.find(href=re.compile(r"member.php?"))["href"]
    return re.findall(r"\?(\d*)", link)[0]


def get_urls(searchurl, links=None):
    """
    Recursively get posts links from searchurl.

    :param searchurl: Link to the Search page.
    :param links: List of already connected links.
    :return:
    """

    if not links:
        links = []

    b.open(searchurl)
    assert b.response.status_code == 200

    # get links
    tags = b.select("li h3 a")
    links.extend([forum + x["href"] for x in tags])

    if b.find("a", rel="next"):  # has next page
        nextlink = forum + b.find("a", rel="next")["href"]
        return get_urls(nextlink, links)
    else:
        c.executemany("insert or ignore into posts (id, url) values (?,?)", [(idfromlink(x), x) for x in links])
        conn.commit()
        return links


def is_last_search(search):
    """
    Checks if search has less than 60 result pages.
    :param search: URL to search result page.
    :return: Boolean
    """

    b.open(search)
    return b.find(string=re.compile(r"Page 1"))[-2:] != "60"


def idfromlink(link):
    """Get post id from post link."""

    return link.split("#post")[1]


def get_post(postlink):
    """Download post and return id, link, date, title and message of post."""

    postid = idfromlink(postlink)
    print("Downloading post:", postid)

    b.open(postlink)
    try:

        post = b.find(id=re.compile(postid))

        date = post.find(class_="date").get_text().replace("\xa0", " ")
        date = parse(date)

        # If post has no title, take Thread title
        try:
            title = post.h2.text.strip()
        except AttributeError:
            title = b.find("title").text.strip()

        category = b.select("div.breadcrumb li")[-2].text

        message = str(post.blockquote)

        return int(postid), postlink, date, category, title, message

    except Exception as e:
        """Sometimes this fails. I have yet to find why. So for now, here's an ugly workaround,"""

        print("ERROR:", postid)
        return int(postid), postlink, None, None, str(e), b.response.text


if __name__ == "__main__":
    args = docopt(__doc__)

    userid = login(args["USERNAME"], args["PASSWORD"])

    oldest = 0

    while True:

        # Build Search url
        search = forum + searchbase.format(userid, oldest)

        print("Collecting links:\n\t", search)

        # get links
        links = get_urls(search)

        # get posts
        for link in links[-1:]:
            post = get_post(link)
            conn.execute("INSERT OR REPLACE INTO posts VALUES (?,?,?,?,?,?)", post)
            conn.commit()

        if is_last_search(search):
            break
        else:
            # get oldest date in DB
            oldest_date = c.execute('Select min(date) as "ts [timestamp]" from posts').fetchone()[0]
            diff = now - oldest_date
            oldest = diff.days
            sleep(5)

    """
    Ugly work-around for mystery bug.

    TODO
    """

    print("Link collection done.")
    print("Starting post scrape...")
    for x in c.execute("select url from posts").fetchall():
        post = get_post(x[0])
        conn.execute("insert or replace into posts values (?,?,?,?,?,?)", post)
        conn.commit()

    print("All posts saved.")
