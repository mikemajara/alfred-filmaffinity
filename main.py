#!/usr/bin/python
# encoding: utf-8

import os
import re
import sys
import urllib
from time import time

from bs4 import BeautifulSoup

from workflow import Workflow3, web

DISPLAY_DETAILS = os.getenv('MM_DISPLAY_DETAILS').isdigit() and int(os.getenv('MM_DISPLAY_DETAILS'))
DISPLAY_THUMBNAILS = os.getenv('MM_DISPLAY_THUMBNAILS').isdigit() and int(os.getenv('MM_DISPLAY_THUMBNAILS'))

if DISPLAY_DETAILS or DISPLAY_THUMBNAILS:
    from pyquery import PyQuery as pq

URL_SEARCH_GET = "https://www.filmaffinity.com/es/search.php?stype=title&stext="
URL_SEARCH_POST = "https://www.filmaffinity.com/es/search-ac.ajax.php?action=searchTerm&term="
ICON_DEFAULT = "icon.png"

def get_filmaffinity_suggestions(word):
    url = "https://www.filmaffinity.com/es/search-ac.ajax.php?action=searchTerm&term=" + urllib.quote(word)
    return web.post(url)


def get_raw_html_for_url(url):
    res = web.get(url)
    return res.text if res.status_code == 200 else None


def get_url_for_film_id(id):
    return "https://www.filmaffinity.com/es/film" + str(id) + ".html"


def get_film_detail_string(id):
    try:
        html_raw = get_raw_html_for_url(get_url_for_film_id(id))
        if html_raw is None:
            return None

        t1 = time()
        soup = BeautifulSoup(html_raw, 'html.parser')
        rating_node = soup.find(id='movie-rat-avg')
        t2 = time()
        elapsed1 = t2 - t1
        # print('Elapsed time is %f seconds.' % elapsed1)

        t1 = time()
        d = pq(html_raw)        
        rating_node = d('div#movie-rat-avg')
        t2 = time()
        elapsed2 = t2 - t1
        # print('Elapsed time is %f seconds.' % elapsed2)

        if rating_node is not None:
            rating_str = (rating_node.attr('content') or "-") + "/10. bs4: " + str(round(elapsed1, 4)) + "s. pq" + str(round(elapsed2, 4)) + "s. "  
        
        return rating_str
    except e:
        print("Unexpected exception")
        return ""


def download_image_from_url(url):
    save_directory = './cache'
    try:
        filename = os.path.basename(url)
        filepath = os.path.join(save_directory, filename)
        web.get(url).save_to_path(filepath)
        return filename, filepath
    except:
        print("Unexpected exception") # On error fall back to defaults
        return ICON_DEFAULT, os.path.join('.', ICON_DEFAULT)


def is_result_type_movie(result):
    return re.search(r"movie-card-ac", result['label']) is not None


def main(wf):    
    args = wf.args
    searchString = ' '.join(args)
    
    if (len(args) > 0):
        res = get_filmaffinity_suggestions(searchString).json()
        for result in res['results']:
            if not is_result_type_movie(result):
                continue

            # defaults 
            filename, filepath = ICON_DEFAULT, os.path.join('.', ICON_DEFAULT)
            subtitle = ""

            if DISPLAY_THUMBNAILS:
                d = pq(result['label'])
                thumbnail_uri = d('div img').attr('src')
                if thumbnail_uri is not None:
                    filename, filepath = download_image_from_url(thumbnail_uri)

            if DISPLAY_DETAILS:
                subtitle = get_film_detail_string(result['id'])
            
            wf.add_item(
                title=result['value'].encode('ascii', 'replace'),
                subtitle=subtitle,
                arg=get_url_for_film_id(result['id']),
                valid=True,
                icon=filepath
            )

    # Default option to search if no result found
    wf.add_item(
        title="Search",
        subtitle="Search filmaffinity for " + " ".join(args),
        arg="https://www.filmaffinity.com/es/advsearch2.php?q=" + urllib.quote(searchString),
        valid=True,
        icon=ICON_DEFAULT
    )

    # --- 
    # Send output to Alfred. You can only call this once.
    # Well, you *can* call it multiple times, but subsequent calls
    # are ignored (otherwise the JSON sent to Alfred would be invalid).
    # ----
    wf.send_feedback()


if __name__ == '__main__':
    # Create a global `Workflow3` object
    wf = Workflow3()
    # Call your entry function via `Workflow3.run()` to enable its
    # helper functions, like exception catching, ARGV normalization,
    # magic arguments etc.
    sys.exit(wf.run(main))