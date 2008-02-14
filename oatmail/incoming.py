import errno
import logging
import os

from oatmail import (
    maildir,
    spamminess,
    )

log = logging.getLogger('oatmail.incoming')

def process(
    maildepot,
    _qsf=None,
    ):
    """
    Process all emails in maildir at C{path}.

    Processing includes spam checks.
    """
    incoming_path = os.path.join(maildepot, 'incoming')
    for path in maildir.walk(incoming_path):
        rating = spamminess.spamminess(
            path=os.path.join(incoming_path, path),
            _qsf=_qsf,
            )
        if rating is None:
            log.debug('Miss %s', path)
            continue
        if rating > 90:
            log.info('Spam %-3d%% %s', rating, path)
            rounded_rating = int(round(rating/5.0)) * 5
            folder = 'INBOX.spam.%d' % rounded_rating
        else:
            log.info('Ham  %-3d%% %s', rating, path)
            folder = 'INBOX'

        maildir.create(os.path.join(maildepot, folder))
        old_path = os.path.join(
            incoming_path,
            path,
            )
        new_path = os.path.join(
            maildepot,
            folder,
            path,
            )
        log.debug('Move %s to %s', old_path, new_path)
        try:
            os.rename(old_path, new_path)
        except OSError, e:
            if e.errno == errno.ENOENT:
                # lost a race
                pass
            else:
                raise

def __main__(args):
    import optparse

    logging.basicConfig(level=logging.INFO)
    parser = optparse.OptionParser(
        usage='%prog [OPTS] DEPOT'
        )
    opts, args = parser.parse_args(args[1:])

    try:
        (depot,) = args
    except ValueError:
        parser.error('missing DEPOT.')

    process(maildepot=depot)
