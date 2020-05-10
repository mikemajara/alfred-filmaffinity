#!/usr/bin/python
# encoding: utf-8

import os
import re
import sys
import json
import urllib
from time import time

import cache
from workflow import Workflow3, web
from workflow.background import run_in_background, is_running

DISPLAY_DETAILS = os.getenv('MM_DISPLAY_DETAILS').isdigit() and int(os.getenv('MM_DISPLAY_DETAILS'))
DISPLAY_THUMBNAILS = os.getenv('MM_DISPLAY_THUMBNAILS').isdigit() and int(os.getenv('MM_DISPLAY_THUMBNAILS'))
REFRESH_RATE = 0.2
DEFAULT_LANGUAGE = 'en'

URL_SEARCH_GET = "https://www.filmaffinity.com/"+DEFAULT_LANGUAGE+"/search.php?stype=title&stext="
URL_SEARCH_POST = "https://www.filmaffinity.com/"+DEFAULT_LANGUAGE+"/search-ac.ajax.php?action=searchTerm&term="
ICON_DEFAULT = "icon.png"

def get_filmaffinity_suggestions(word):
    url = "https://www.filmaffinity.com/"+DEFAULT_LANGUAGE+"/search-ac.ajax.php?action=searchTerm&term=" + urllib.quote(word)
    return web.post(url)


def get_url_for_film_id(id):
    return "https://www.filmaffinity.com/"+DEFAULT_LANGUAGE+"/film" + str(id) + ".html"


def is_result_type_movie(result):
    return re.search(r"movie-card-ac", result['label']) is not None


def main(wf):

    if DISPLAY_DETAILS or DISPLAY_THUMBNAILS:
        from pyquery import PyQuery as pq

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
            valid = True
            details = ""
            
            # quick access
            film_id_str = str(result['id'])

            if DISPLAY_DETAILS:
                details = wf.cached_data(film_id_str, max_age=0)
                if details is None:
                    run_in_background(
                        'update_details_' + film_id_str,
                        [
                            '/usr/bin/python',
                            wf.workflowfile('update_details.py'),
                            film_id_str
                        ]
                    )
                    details = "Loading details... "
                    wf.rerun = REFRESH_RATE
                    
            if DISPLAY_THUMBNAILS:
                filepath = cache.get(film_id_str)
                if filepath is None:
                    run_in_background(
                        'update_thumbnail_' + film_id_str,
                        ['/usr/bin/python',
                        wf.workflowfile('update_thumbnails.py'),
                        json.dumps(result)]
                    )
                    details += "Loading thumbnail... "
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
    wf = Workflow3(libraries=[os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))])
    # wf = Workflow3(libraries=[os.path.join(os.path.dirname(__file__), 'lib')])
    log = wf.logger
    # Call your entry function via `Workflow3.run()` to enable its
    # helper functions, like exception catching, ARGV normalization,
    # magic arguments etc.
    sys.exit(wf.run(main))