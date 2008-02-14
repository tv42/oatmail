import os

from nose.tools import (
    eq_ as eq,
    )
from oatmail.test.util import (
    assert_raises,
    maketemp,
    writeFile,
    )

from oatmail import spamminess

def test_file_not_found():
    tmp = maketemp()
    path = os.path.join(tmp, 'does-not-exist')
    got = spamminess.spamminess(
        path=path,
        _qsf='should-not-be-run',
        )
    eq(got, None)

def test_fail():
    tmp = maketemp()
    mockqsf = os.path.join(tmp, 'mock-qsf')
    writeFile(
        mockqsf,
        """\
#!/bin/sh
exit 42
""")
    os.chmod(mockqsf, 0755)
    message = os.path.join(tmp, 'fake-email')
    writeFile(
        message,
        'fake email',
        )
    e = assert_raises(
        RuntimeError,
        spamminess.spamminess,
        path=message,
        _qsf=mockqsf,
        )
    eq(str(e), 'qsf failed: 42')

def test_ok_spam82():
    tmp = maketemp()
    mockqsf = os.path.join(tmp, 'mock-qsf')
    writeFile(
        mockqsf,
        """\
#!/bin/sh
test "$#" = "2"
test "$1" = "--test"
test "$2" = "--rating"
test "$(cat)" = "fake-email"
echo 82
exit 1
""")
    os.chmod(mockqsf, 0755)
    message = os.path.join(tmp, 'fake-email')
    writeFile(
        message,
        'fake email',
        )
    got = spamminess.spamminess(
        path=message,
        _qsf=mockqsf,
        )
    eq(got, 82)

def test_ok_ham34():
    tmp = maketemp()
    mockqsf = os.path.join(tmp, 'mock-qsf')
    writeFile(
        mockqsf,
        """\
#!/bin/sh
test "$#" = "2"
test "$1" = "--test"
test "$2" = "--rating"
test "$(cat)" = "fake-email"
echo 34
exit 0
""")
    os.chmod(mockqsf, 0755)
    message = os.path.join(tmp, 'fake-email')
    writeFile(
        message,
        'fake email',
        )
    got = spamminess.spamminess(
        path=message,
        _qsf=mockqsf,
        )
    eq(got, 34)
