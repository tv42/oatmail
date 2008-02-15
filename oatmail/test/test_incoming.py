import os
import ConfigParser

from nose.tools import eq_ as eq

from oatmail.test.util import (
    assert_raises,
    maketemp,
    writeFile,
    readFile,
    )

from oatmail import (
    incoming,
    maildir,
    )

def test_process_empty():
    tmp = maketemp()
    incoming_path = os.path.join(tmp, 'incoming')
    maildir.create(incoming_path)
    cfg = ConfigParser.RawConfigParser()
    cfg.add_section('depot %s' % tmp)
    incoming.process(cfg=cfg)

def test_process_ham():
    tmp = maketemp()
    depot = os.path.join(tmp, 'depot')
    os.mkdir(depot)
    incoming_path = os.path.join(depot, 'incoming')
    maildir.create(incoming_path)
    writeFile(
        os.path.join(
            incoming_path,
            'new',
            '1202936960.V801I880d5M358047.foo',
            ),
        'fake email',
        )
    mockqsf = os.path.join(tmp, 'mock-qsf')
    writeFile(
        mockqsf,
        """\
#!/bin/sh
test "$#" = "2"
test "$1" = "--test"
test "$2" = "--rating"
test "$(cat)" = "fake email"
echo 34
exit 0
""")
    os.chmod(mockqsf, 0755)
    cfg = ConfigParser.RawConfigParser()
    cfg.add_section('qsf')
    cfg.set('qsf', 'path',  mockqsf)
    cfg.add_section('depot %s' % depot)
    cfg.add_section('rules incoming')
    cfg.set(
        'rules incoming',
        'spam all',
        'INBOX.spam.%(spamminess_percentage)d',
        )
    incoming.process(cfg)
    folder = 'INBOX'
    eq(
        sorted(os.listdir(depot)),
        sorted(['incoming', folder]),
        )
    eq(
        list(maildir.walk(os.path.join(depot, 'incoming'))),
        [],
        )
    path = os.path.join(depot, folder)
    eq(
        list(maildir.walk(path)),
        [
            'new/1202936960.V801I880d5M358047.foo',
            ],
        )
    eq(
        readFile(os.path.join(
                path,
                'new',
                '1202936960.V801I880d5M358047.foo',
                )),
        'fake email',
        )

def test_process_spam():
    tmp = maketemp()
    depot = os.path.join(tmp, 'depot')
    os.mkdir(depot)
    incoming_path = os.path.join(depot, 'incoming')
    maildir.create(incoming_path)
    writeFile(
        os.path.join(
            incoming_path,
            'new',
            '1202936960.V801I880d5M358047.foo',
            ),
        'fake email',
        )
    mockqsf = os.path.join(tmp, 'mock-qsf')
    writeFile(
        mockqsf,
        """\
#!/bin/sh
test "$#" = "2"
test "$1" = "--test"
test "$2" = "--rating"
test "$(cat)" = "fake email"
echo 97
exit 1
""")
    os.chmod(mockqsf, 0755)
    cfg = ConfigParser.RawConfigParser()
    cfg.add_section('qsf')
    cfg.set('qsf', 'path',  mockqsf)
    cfg.add_section('depot %s' % depot)
    cfg.add_section('rules incoming')
    cfg.set(
        'rules incoming',
        'spam all',
        'INBOX.spam.%(spamminess_percentage_rounded_5)d',
        )
    incoming.process(cfg)
    folder = 'INBOX.spam.95'
    eq(
        sorted(os.listdir(depot)),
        sorted(['incoming', folder]),
        )
    eq(
        list(maildir.walk(os.path.join(depot, 'incoming'))),
        [],
        )
    path = os.path.join(depot, folder)
    eq(
        list(maildir.walk(path)),
        [
            'new/1202936960.V801I880d5M358047.foo',
            ],
        )
    eq(
        readFile(os.path.join(
                path,
                'new',
                '1202936960.V801I880d5M358047.foo',
                )),
        'fake email',
        )

def test_process_listid():
    tmp = maketemp()
    depot = os.path.join(tmp, 'depot')
    os.mkdir(depot)
    incoming_path = os.path.join(depot, 'incoming')
    maildir.create(incoming_path)
    MAILBODY = """\
From: bar
To: foo
List-ID: Users of FOO <FOO-users.lists.example.COM>
Subject: foo

foo
"""
    writeFile(
        os.path.join(
            incoming_path,
            'new',
            '1202936960.V801I880d5M358047.foo',
            ),
        MAILBODY,
        )
    cfg = ConfigParser.RawConfigParser()
    cfg.add_section('depot %s' % depot)
    cfg.add_section('rules incoming')
    cfg.set(
        'rules incoming',
        'angle-bracket-header liST-id foo-USERS.lists.EXAMPLE.com',
        'list.foo',
        )
    incoming.process(cfg)
    folder = 'list.foo'
    eq(
        sorted(os.listdir(depot)),
        sorted(['incoming', folder]),
        )
    eq(
        list(maildir.walk(os.path.join(depot, 'incoming'))),
        [],
        )
    path = os.path.join(depot, folder)
    eq(
        list(maildir.walk(path)),
        [
            'new/1202936960.V801I880d5M358047.foo',
            ],
        )
    eq(
        readFile(os.path.join(
                path,
                'new',
                '1202936960.V801I880d5M358047.foo',
                )),
        MAILBODY,
        )

def test_process_newline():
    # line wrapping in the config file can cause extra whitespace in
    # the value; this affects all rules but testing with this one
    tmp = maketemp()
    depot = os.path.join(tmp, 'depot')
    os.mkdir(depot)
    incoming_path = os.path.join(depot, 'incoming')
    maildir.create(incoming_path)
    MAILBODY = """\
From: bar
To: foo
List-ID: Users of FOO <FOO-users.lists.example.COM>
Subject: foo

foo
"""
    writeFile(
        os.path.join(
            incoming_path,
            'new',
            '1202936960.V801I880d5M358047.foo',
            ),
        MAILBODY,
        )
    cfg = ConfigParser.RawConfigParser()
    cfg.add_section('depot %s' % depot)
    cfg.add_section('rules incoming')
    cfg.set(
        'rules incoming',
        'angle-bracket-header liST-id foo-USERS.lists.EXAMPLE.com',
        '\nlist.foo\n',
        )
    incoming.process(cfg)
    folder = 'list.foo'
    eq(
        sorted(os.listdir(depot)),
        sorted(['incoming', folder]),
        )
    eq(
        list(maildir.walk(os.path.join(depot, 'incoming'))),
        [],
        )
    path = os.path.join(depot, folder)
    eq(
        list(maildir.walk(path)),
        [
            'new/1202936960.V801I880d5M358047.foo',
            ],
        )
    eq(
        readFile(os.path.join(
                path,
                'new',
                '1202936960.V801I880d5M358047.foo',
                )),
        MAILBODY,
        )

