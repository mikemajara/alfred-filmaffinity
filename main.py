#!/usr/bin/python
# encoding: utf-8

import os
import re
import sys
import urllib
from time import time

import cache
from workflow import Workflow3, web
from workflow.background import run_in_background, is_running

DISPLAY_DETAILS = os.getenv('MM_DISPLAY_DETAILS').isdigit() and int(os.getenv('MM_DISPLAY_DETAILS'))
DISPLAY_THUMBNAILS = os.getenv('MM_DISPLAY_THUMBNAILS').isdigit() and int(os.getenv('MM_DISPLAY_THUMBNAILS'))
REFRESH_RATE = 0.5

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

        d = pq(html_raw)        
        rating_node = d('div#movie-rat-avg')

        if rating_node is not None:
            rating_str = (rating_node.attr('content') or "-") + "/10 "
        
        return rating_str
    except e:
        log.debug("Unexpected exception")
        return ""

def is_result_type_movie(result):
    return re.search(r"movie-card-ac", result['label']) is not None


def main(wf):    
    args = wf.args
    searchString = ' '.join(args)
    
    if (len(args) > 0):
        res = wf.cached_data(searchString, max_age=0)
        if res is None:
            res = get_filmaffinity_suggestions(searchString).json()
            wf.cache_data(searchString, res)

        for result in res['results']:
            if not is_result_type_movie(result):
                continue

            # defaults 
            filepath = os.path.join('.', ICON_DEFAULT)
            result_id = str(result['id'])
            details = ""
            valid = True


            if DISPLAY_THUMBNAILS:
                file_id = 'thumbnail_' + result_id
                data = cache.load(file_id)
                if data is None:
                    d = pq(result['label'])
                    thumbnail_uri = d('div img').attr('src')
                    if thumbnail_uri is not None:
                        cache.dump(file_id, thumbnail_uri)

                filepath = cache.load(file_id)

            if DISPLAY_DETAILS:
                details = wf.cached_data(result_id, max_age=0)
                if details is None:
                    run_in_background(
                        'update_details_' + result_id,
                        [
                            '/usr/bin/python',
                            wf.workflowfile('update_details.py'),
                            result_id
                        ]
                    )
                    details = "Loading details..."
                    wf.rerun = REFRESH_RATE
                    
            wf.add_item(
                title=result['value'].encode('ascii', 'replace'),
                subtitle=details,
                arg=get_url_for_film_id(result['id']),
                valid=valid,
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
    log = wf.logger
    # Call your entry function via `Workflow3.run()` to enable its
    # helper functions, like exception catching, ARGV normalization,
    # magic arguments etc.
    sys.exit(wf.run(main))