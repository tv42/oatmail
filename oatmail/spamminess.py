from __future__ import with_statement

import errno
import logging
import subprocess
import sys

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
