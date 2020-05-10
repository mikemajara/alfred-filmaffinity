# encoding: utf-8

import os
import sys
import json
import cache
from workflow import Workflow3, web


def get_thumbnail_url(film_dict):
    d = pq(film_dict['label'])
    return d('div img').attr('src')

def main(wf):


    args = wf.args
    film_dict = json.loads(str(args[0]))
    film_id = str(film_dict['id'])
    

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
        
    
if __name__ == '__main__':
    wf = Workflow3(libraries=[os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))])
    from pyquery import PyQuery as pq # define immediately after for global use
    log = wf.logger
    wf.run(main)