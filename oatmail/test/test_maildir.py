import os

from nose.tools import (
    eq_ as eq,
    )
from oatmail.test.util import (
    assert_raises,
    maketemp,
    writeFile,
    )

from oatmail import maildir

def test_walk_empty():
    tmp = maketemp()
    os.mkdir(os.path.join(tmp, 'new'))
    os.mkdir(os.path.join(tmp, 'cur'))
    g = maildir.walk(tmp)
    assert_raises(StopIteration, g.next)

def test_walk_simple_new():
    tmp = maketemp()
    os.mkdir(os.path.join(tmp, 'new'))
    os.mkdir(os.path.join(tmp, 'cur'))
    writeFile(
        os.path.join(tmp, 'new', '1202936960.V801I880d5M358047.foo'),
        'fake email',
        )
    g = maildir.walk(tmp)
    eq(g.next(), os.path.join('new', '1202936960.V801I880d5M358047.foo'))
    assert_raises(StopIteration, g.next)

def test_walk_simple_cur():
    tmp = maketemp()
    os.mkdir(os.path.join(tmp, 'new'))
    os.mkdir(os.path.join(tmp, 'cur'))
    writeFile(
        os.path.join(tmp, 'cur', '1202936960.V801I880d5M358047.foo:2,'),
        'fake email',
        )
    g = maildir.walk(tmp)
    eq(g.next(), os.path.join('cur', '1202936960.V801I880d5M358047.foo:2,'))
    assert_raises(StopIteration, g.next)

def test_walk_simple_both():
    tmp = maketemp()
    os.mkdir(os.path.join(tmp, 'new'))
    os.mkdir(os.path.join(tmp, 'cur'))
    writeFile(
        os.path.join(tmp, 'cur', '1202936960.V801I880d5M358047.foo:2,'),
        'fake email',
        )
    writeFile(
        os.path.join(tmp, 'new', '1196638757.V801Ia938aM515340.eagain'),
        'fake email',
        )
    g = maildir.walk(tmp)
    eq(g.next(), os.path.join('cur', '1202936960.V801I880d5M358047.foo:2,'))
    eq(g.next(), os.path.join('new', '1196638757.V801Ia938aM515340.eagain'))
    assert_raises(StopIteration, g.next)
