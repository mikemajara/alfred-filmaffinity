# encoding: utf-8

import os
import sys
import json
from workflow import Workflow3, web

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


def main(wf):
    args = wf.args
    details = get_film_detail_string(args[0])
    log.debug('caching: ' + args[0] + " -- " + details)
    wf.cache_data(args[0], details)
    
if __name__ == '__main__':
    wf = Workflow3(libraries=[os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))])
    from pyquery import PyQuery as pq # define immediately after for global use
    log = wf.logger
    wf.run(main)