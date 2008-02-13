import os

def walk(path):
    """
    Generate relative pathnames of files stored in maildir C{path}.
    """
    for subdir in ['cur', 'new']:
        for filename in os.listdir(os.path.join(path, subdir)):
            yield os.path.join(subdir, filename)

