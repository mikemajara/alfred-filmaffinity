
#!/usr/bin/python
# encoding: utf-8

import sys
import os
import urllib

# Workflow3 supports Alfred 3's new features. The `Workflow` class
# is also compatible with Alfred 2.
from workflow import Workflow3, web
from bs4 import BeautifulSoup

URL_SEARCH_GET = "https://www.filmaffinity.com/es/advsearch2.php?q="
URL_SEARCH_POST = "https://www.filmaffinity.com/es/search-ac.ajax.php?action=searchTerm&term="
ICON_DEFAULT = "icon.png"

def get_filmaffinity_suggestions(word):
    url = "https://www.filmaffinity.com/es/search-ac.ajax.php?action=searchTerm&term=" + urllib.quote(word)
    return web.post(url)

def get_filmaffinity_html(url):
    res = web.get(url)

    return res.text if res.status_code == 200 else None

def get_film_url(id):
    # print('getting url for film ' + str(id))
    return "https://www.filmaffinity.com/es/film" + str(id) + ".html"

def crawl_filmaffinity_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    rating_element = soup.find(id='movie-rat-avg')
    rating = rating_element.attrs['content'] if rating_element is not None else None
    return {
        'rating': rating
    }

def main(wf):
    # The Workflow3 instance will be passed to the function
    # you call from `Workflow3.run`.
    # Not super useful, as the `wf` object created in
    # the `if __name__ ...` clause below is global...
    #
    # Your imports go here if you want to catch import errors, which
    # is not a bad idea, or if the modules/packages are in a directory
    # added via `Workflow3(libraries=...)`

    from pyquery import PyQuery as pq
    # import amodule
    # import anothermodule

    # Get args from Workflow3, already in normalized Unicode.
    # This is also necessary for "magic" arguments to work.
    args = wf.args
    searchString = ' '.join(args)
    # Do stuff here ...
    # print("searching for " + args[0])
    
    if (len(args) > 0):
        res = get_filmaffinity_suggestions(searchString).json()
        for result in res['results']:
            if not isinstance(result['id'], int):
                continue
            d = pq(result['label'])
            thumbnail_uri = d('div img').attr('src')
            
            html_raw = get_filmaffinity_html(get_film_url(result['id']))

            if html_raw is None:
                continue

            film_attributes = crawl_filmaffinity_html(html_raw)

            # no thumbnail - default
            filename = ICON_DEFAULT
            filepath = os.path.join('./cache', filename)

            # there is a thumbnail -
            if thumbnail_uri is not None:
                filename = os.path.basename(thumbnail_uri)
                filepath = os.path.join('./cache', filename)
                web.get(thumbnail_uri).save_to_path(filepath)

            # attributes
            rating_str = "-" if film_attributes['rating'] is None else film_attributes['rating'] + "/10"
            
            wf.add_item(
                title=result['value'].encode('ascii', 'replace'),
                subtitle=u"Nota: "+rating_str,
                arg=get_film_url(result['id']),
                valid=True,
                icon=filepath
            )

    # Add default option to search if no result found

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