from __future__ import with_statement

import errno
import logging
import os
import ConfigParser

from oatmail import (
    maildir,
    spamminess,
    matcher,
    )

log = logging.getLogger('oatmail.incoming')

def process(cfg):
    """
    Process all new emails as according to C{cfg}.

    @param cfg: the configuration

    @type cfg: ConfigParser.SafeConfigParser
    """

    for section in cfg.sections():
        l = section.split(None, 1)
        if l[0] != 'depot':
            continue
        depot = l[1]
        depot = os.path.expanduser(depot)
        log.info('Depot %s', depot)

        def g():
            found = False
            for var, rules_name in cfg.items(section):
                l = var.split(None, 1)
                if l[0] != 'process':
                    continue
                found = True
                incoming_folder = l[1]
                yield (incoming_folder, rules_name)
            if not found:
                yield ('incoming', 'incoming')

        for incoming_folder, rules_name in g():
            log.info(
                'Incoming folder %r using rules %r',
                incoming_folder,
                rules_name,
                )
            incoming_path = os.path.join(depot, incoming_folder)
            for path in maildir.walk(incoming_path):
                # default folder if nothing matches
                folder = 'INBOX'

                for k,v in cfg.items('rules %s' % rules_name):
                    l = k.split(None)
                    name = l[0]

                    data = matcher.call_matcher(
                        name=name,
                        cfg=cfg,
                        depot=depot,
                        folder=incoming_folder,
                        path=path,
                        args=l[1:],
                        )

                    if data is not None:
                        log.debug('Matcher data: %r', data)
                        folder = v.strip() % data
                        break

                maildir.create(os.path.join(depot, folder))
                old_path = os.path.join(
                    incoming_path,
                    path,
                    )
                new_path = os.path.join(
                    depot,
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


def __main__(args=None):
    import optparse
    import sys

    if args is None:
        args = sys.argv

    logging.basicConfig(level=logging.INFO)
    parser = optparse.OptionParser(
        usage='%prog [OPTS]'
        )
    parser.add_option(
        '-c', '--config',
        help='Read configuration from file (default %default)',
        metavar='FILE',
        )
    parser.set_defaults(
        config=os.path.expanduser('~/.oatmail.conf'),
        )
    opts, args = parser.parse_args(args[1:])

    cfg = ConfigParser.RawConfigParser()
    with file(opts.config) as f:
        cfg.readfp(f)

    if args:
        parser.error('did not expect command line arguments.')

    process(cfg)
