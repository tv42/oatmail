#!/usr/bin/python
from setuptools import setup, find_packages
import os

setup(
    name = "oatmail",
    version = "0.1",
    packages = find_packages(),

    author = "Tommi Virtanen",
    author_email = "tv@eagain.net",
    description = "synchronizing Maildir mail with git",
#     long_description = """

# TODO

# """.strip(),
    license = "No public licensing; contact author",
    keywords = "email maildir git",
    url = "http://eagain.net/software/oatmail/",

    entry_points = {
        'console_scripts': [
            'oatmail-incoming = oatmail.incoming:__main__',
            ],
        'oatmail.matcher': [
            'spam = oatmail.spamminess:match_spam',
            'angle-bracket-header = oatmail.categorize:match_angle_bracket_header',
            'all = oatmail.categorize:match_all',
            ],
        },

    test_suite = 'nose.collector'

    )

