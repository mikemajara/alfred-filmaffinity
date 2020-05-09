import os, shutil
from workflow import web
SAVE_DIR = './cache'

def dump(file_id, url):
    save_directory = SAVE_DIR
    try:
        _, ext = os.path.splitext(os.path.basename(url))
        filepath = os.path.join(save_directory, file_id)#, ext) # <- Let's try without extension it might work :)
        web.get(url).save_to_path(filepath)
        return filepath
    except:
        print("Unexpected exception") # On error fall back to defaults
        return ICON_DEFAULT, os.path.join('.', ICON_DEFAULT)

def load(file_id):
    filepath = os.path.join(SAVE_DIR, file_id)
    return filepath if os.path.isfile(filepath) else None

def clear():
    for filename in os.listdir(SAVE_DIR):
        file_path = os.path.join(SAVE_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))