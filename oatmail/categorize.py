from __future__ import with_statement

import email
import os
import re

ANGLE_BRACKETED_RE = re.compile(r'^[^<>]*<\s*([^<>\s]+)\s*>[^<>]*$')

def get_angle_bracketed_header(message, header):
    """
    Extract an angle bracketed header from the message.

    Will strip any commentary and angle brackets and lowercase the
    string.

    @param message: the message

    @type message: email.Message.Message

    @param header: header to extract, case is irrelevant

    @type header: str

    @returns: the string inside the angle brackets or None

    @rtype: str or None
    """
    value = message[header]
    if value is None:
        return None
    match = ANGLE_BRACKETED_RE.match(value)
    if match is None:
        return None
    content = match.group(1)
    content = content.lower()
    return content

def match_angle_bracket_header(
    cfg,
    depot,
    folder,
    path,
    args,
    ):
    (header, wanted) = args
    with file(os.path.join(depot, folder, path)) as f:
        msg = email.message_from_file(f)
    got = get_angle_bracketed_header(
        message=msg,
        header=header,
        )
    if got is None:
        return None
    if got != wanted.lower():
        return None
    return dict()

def match_all(
    cfg,
    depot,
    folder,
    path,
    args,
    ):
    assert not args
    return dict()
