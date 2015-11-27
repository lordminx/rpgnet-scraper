"""RPGnet Scraper.

Usage:
    scraper.py USERNAME PASSWORD
    scraper.py [options]

Options:
    -h --help       Show this help text."""

from docopt import docopt
from robobrowser import RoboBrowser
from pickle import dump, load
import re
from collections import defaultdict
from dateutil.parser import parse
from datetime import datetime
from time import sleep


# SETUP
forum = "http://forum.rpg.net/"
b = RoboBrowser(user_agent="Firefox", history=False)
now = datetime.now()

searchbase = "search.php?do=finduser&userid={}&contenttype=vBForum_Post&showposts=1&searchdate={}&beforeafter=before"

# LOGIN

def login(USERNAME, PASSWORD):

    b.open(forum + "login.php?do=login")

    print("Trying to login")
    loginform = b.get_form()

    loginform["vb_login_username"] = USERNAME
    loginform["vb_login_password"] = PASSWORD

    loginform.serialize()

    b.submit_form(loginform)

    assert b.response.status_code == 200

    print("Logged in.")

    # get user id
    b.open("http://forum.rpg.net")
    link = b.find(href=re.compile(r"member.php?"))["href"]
    return re.findall(r"\?(\d*)", link)[0]

def get_urls(searchurl, links=[]):
    """Recursively get posts links from searchurl."""

    b.open(searchurl)
    assert b.response.status_code == 200

    # get links
    tags = b.select("li h3 a")
    links.extend([forum + x["href"] for x in tags ])

    if b.find("a", rel="next"): # has next page
        nextlink = forum + b.find("a", rel="next")["href"]
        return get_urls(nextlink, links)
    else:
        return links


def is_last_search(search):
    """Checks if search has less than 60 result pages."""

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

    post = b.find(id=re.compile(postid))

    date = post.find(class_="date").get_text().replace("\xa0", " ")

    # If post has no title, take Thread title
    try:
        title = post.h2.text.strip()
    except AttributeError:
        title = b.find("title").text.strip()

    message = str(post.blockquote)

    return (postid, postlink, date, title, message)

def post_age(post):
    date = parse(post[2])
    age = now - date

    return age.days




if __name__ == "__main__":
    args = docopt(__doc__)

    userid = login(args["USERNAME"], args["PASSWORD"])

    results = []
    oldest = 0

    while True:
        # Build Search url
        search = forum + searchbase.format(userid, oldest)

        print("Collecting links...")
        # get links
        links = get_urls(search)

        # get posts
        results.extend([get_post(link) for link in links])

        if is_last_search(search):
            break
        else:
            oldest = post_age(results[-1])
            sleep(5)

    print("Saving posts...")
    with open("RPGnet-post-archive.pickle", "wb") as f:
        dump(results)
    print("{} posts saved.".len(results))
    runtime = datetime.now() - now
    print("Runtime: {} second".format(runtime.seconds))
