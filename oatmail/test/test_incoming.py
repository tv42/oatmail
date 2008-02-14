import os

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
    incoming.process(maildepot=tmp)

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
    incoming.process(
        maildepot=depot,
        _qsf=mockqsf,
        )
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
    incoming.process(
        maildepot=depot,
        _qsf=mockqsf,
        )
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
