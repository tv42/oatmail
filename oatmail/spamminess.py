from __future__ import with_statement

import errno
import logging
import os
import subprocess
import sys
import ConfigParser

from oatmail import matcher

log = logging.getLogger('oatmail.spamminess')
log_qsf = logging.getLogger('oatmail.spamminess.qsf')

def spamminess(
    path,
    _qsf=None,
    ):
    if _qsf is None:
        _qsf = 'qsf'
    log_qsf.debug('Running qsf on %r', path)
    try:
        msg = file(path)
    except IOError, e:
        if e.errno == errno.ENOENT:
            return None
        else:
            raise
    with msg as msg:
        child = subprocess.Popen(
            [
                _qsf,
                '--test',
                '--rating',
                ],
            close_fds=True,
            stdin=msg,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            )
        rating = child.stdout.readline()
        if rating == '':
            # message was too big for qsf, it skipped processing
            # assume ham
            log_qsf.debug('Too big to check')
            rating = 0
        else:
            rating = int(rating)
            log_qsf.debug('Spamminess %d%%', rating)
        # ignore any other output, while complaining
        for line in child.stdout:
            log_qsf.warn('qsf extra stdout: %r', line)
        returncode = child.wait()
        if returncode in [0, 1]:
            return rating
        else:
            raise RuntimeError(
                'qsf failed: %r' % returncode)

def match_spam(
    cfg,
    depot,
    folder,
    path,
    args,
    ):
    try:
        qsf = cfg.get('qsf', 'path')
    except (ConfigParser.NoSectionError,
            ConfigParser.NoOptionError):
        qsf = None

    rating = spamminess(
        path=os.path.join(depot, folder, path),
        _qsf=qsf,
        )
    if rating is None:
        log.debug('Miss %s', path)
        return None
    if rating > 90:
        log.info('Spam %-3d%% %s', rating, path)
        rounded_rating = int(round(rating/5.0)) * 5
        data = matcher.call_matcher(
            name=args[0],
            cfg=cfg,
            depot=depot,
            folder=folder,
            path=path,
            args=args[1:],
            )
        if data is not None:
            data.update(
                spamminess_percentage=rating,
                spamminess_percentage_rounded_5=rounded_rating,
                )
        return data
    else:
        log.info('Ham  %-3d%% %s', rating, path)
        return None
