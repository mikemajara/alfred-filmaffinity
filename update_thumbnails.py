# encoding: utf-8

import sys
import json
import cache
from pyquery import PyQuery as pq
from workflow import Workflow, web

def get_thumbnail_url(film_dict):
    d = pq(film_dict['label'])
    return d('div img').attr('src')

def main(wf):
    # log.info("------------ entering UPDATE_THUMBNAILS ------------")
    args = wf.args
    film_dict = json.loads(str(args[0]))
    film_id = str(film_dict['id'])
    # log.info('caching for film ' + film_id)

    url = get_thumbnail_url(film_dict)
    if url is not None:
        try:
            filepath = cache.put(film_id, url)
            log.info('cached in path ' + filepath)
        except Exception as e:
            log.error(e)
    else:
        log.info('OMG!! url is None!!')
        return # problem, there is no url for image!
    
    # details = get_film_detail_string(args[0])
    # log.info('-- UPDATE_THUMBNAILS -- ')
    # log.info('caching: ' + json.dumps(film_dict))
    # wf.cache_data(args[0], details)
    
if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    wf.run(main)