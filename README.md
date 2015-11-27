# rpgnet-scraper

A script to download all your RPGnet posts for you. **Don't use this until I fix the memory footprint!**

Usage:
    python scraper.py USERNAME PASSWORD

## Some comments:

* This is very much a work in progress.
* The script is nowhere as fast or efficient as it could be, but I don't want to clobber the RPGnet server.
* If you get the necessary libs (See "requirements.txt".), this should work. No guaranties, though.
* I'm still thinking about the right way to archive the posts for later analysis, so for now they are just a pickled list of tuples.
* Yeah, I'm aware that this is probably **not** the best way to do it. I don't care enough to do something about that at the moment.
