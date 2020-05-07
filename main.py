
#!/usr/bin/python
# encoding: utf-8

import sys

# Workflow3 supports Alfred 3's new features. The `Workflow` class
# is also compatible with Alfred 2.
from workflow import Workflow3
import requests


def get_filmaffinity_suggestions(word):
    url = "https://www.filmaffinity.com/es/search-ac.ajax.php?action=searchTerm&term=" + word
    return requests.post(url).json()


def main(wf):
    # The Workflow3 instance will be passed to the function
    # you call from `Workflow3.run`.
    # Not super useful, as the `wf` object created in
    # the `if __name__ ...` clause below is global...
    #
    # Your imports go here if you want to catch import errors, which
    # is not a bad idea, or if the modules/packages are in a directory
    # added via `Workflow3(libraries=...)`

    import json
    from pyquery import PyQuery as pq
    # import amodule
    # import anothermodule

    # Get args from Workflow3, already in normalized Unicode.
    # This is also necessary for "magic" arguments to work.
    args = wf.args

    # Do stuff here ...
    # print("searching for " + args[0])
    if (len(args) > 0):
        res = get_filmaffinity_suggestions(args[0])
        for result in res[u'results']:

            # print("found" + json.dumps(result, indent=4))
            d = pq(result['label'])
            icon_src = d('div img').attr('src')
            # print(icon_src)
            wf.add_item(
                title=result['value'],
                # subtitle=result['href'],
                arg="https://www.filmaffinity.com/es/film" + str(result['id']) + ".html",
                valid=True,
                icon=icon_src
            )
    # print(json.dumps(results, indent=4))
    # print(args[0])

    # Add an item to Alfred feedback
    # wf.add_item(u'Item title', u'Item subtitle')

    # Send output to Alfred. You can only call this once.
    # Well, you *can* call it multiple times, but subsequent calls
    # are ignored (otherwise the JSON sent to Alfred would be invalid).
    wf.send_feedback()


if __name__ == '__main__':
    # Create a global `Workflow3` object
    wf = Workflow3()
    # Call your entry function via `Workflow3.run()` to enable its
    # helper functions, like exception catching, ARGV normalization,
    # magic arguments etc.
    sys.exit(wf.run(main))