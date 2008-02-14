import os

from oatmail.util import mkdir

def create(path):
    mkdir(path, 0700)
    mkdir(os.path.join(path, 'new'), 0700)
    mkdir(os.path.join(path, 'cur'), 0700)
    mkdir(os.path.join(path, 'tmp'), 0700)

def walk(path):
    """
    Generate relative pathnames of files stored in maildir C{path}.
    """
    for subdir in ['cur', 'new']:
        for filename in os.listdir(os.path.join(path, subdir)):
            yield os.path.join(subdir, filename)

