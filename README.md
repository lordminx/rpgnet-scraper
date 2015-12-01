# rpgnet-scraper

A script to download all your RPGnet posts for you. 

Usage:
    python scraper.py USERNAME PASSWORD

## Some comments:

* This is very much a work in progress.
* It's also way uglier than it could be.
* The script is nowhere as fast or efficient as it could be, but I don't want to clobber the RPGnet server.
* If you get the necessary libs (See "requirements.txt".), this should work. No guaranties, though.
* The script saves the posts in a Sqlite database with the filename "post-archive.db". For every post, it saves the posts id, date, forum category, post title and the message, as well as a link to the post itself.
* There are some unlikely edge cases and weird bugs that happen now and then. Still trying to track down their sources.
* I intent to add additional functionality eventually. Maybe.
* If you want to analyze your posts, you'll need a bit of coding/SQL knowledge, though I intend to push some "Let's look at your archive" scripts soon-ish.

