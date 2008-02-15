from nose.tools import eq_ as eq
import os
import ConfigParser
import email.Message

from oatmail.test.util import (
    maketemp,
    writeFile,
    )

from oatmail import (
    categorize,
    maildir,
    )

def test_list_id_no_header():
    msg = email.Message.Message()
    msg.set_payload('foo')
    got = categorize.get_angle_bracketed_header(msg, 'List-ID')
    eq(got, None)

def test_list_id_no_angle_brackets():
    msg = email.Message.Message()
    msg.add_header('List-ID', 'foo')
    msg.set_payload('foo')
    got = categorize.get_angle_bracketed_header(msg, 'List-ID')
    eq(got, None)

def test_list_id_simple():
    msg = email.Message.Message()
    msg.add_header('List-ID', '<foo.bar.baz>')
    msg.set_payload('foo')
    got = categorize.get_angle_bracketed_header(msg, 'List-ID')
    eq(got, 'foo.bar.baz')

def test_list_id_description():
    msg = email.Message.Message()
    msg.add_header('List-ID', 'description here <foo.bar.baz>')
    msg.set_payload('foo')
    got = categorize.get_angle_bracketed_header(msg, 'List-ID')
    eq(got, 'foo.bar.baz')

def test_list_id_whitespace():
    msg = email.Message.Message()
    msg.add_header('List-ID', 'description here < foo.bar.baz >')
    msg.set_payload('foo')
    got = categorize.get_angle_bracketed_header(msg, 'List-ID')
    eq(got, 'foo.bar.baz')

def test_list_id_uppercase():
    msg = email.Message.Message()
    msg.add_header('List-ID', 'description here <foo.Bar.BAZ>')
    msg.set_payload('foo')
    got = categorize.get_angle_bracketed_header(msg, 'List-ID')
    eq(got, 'foo.bar.baz')

def test_list_bad_internal_whitespace():
    # whitespace within the value is just considered invalid and the
    # header is ignored
    msg = email.Message.Message()
    msg.add_header('List-ID', 'description here <foo.B ar.BAZ>')
    msg.set_payload('foo')
    got = categorize.get_angle_bracketed_header(msg, 'List-ID')
    eq(got, None)

def test_match_angle_bracket_header_simple():
    tmp = maketemp()
    maildir.create(os.path.join(tmp, 'mdir'))
    writeFile(
        os.path.join(tmp, 'mdir', 'new', '1196638757.V801Ia938aM515340.foo'),
        """\
From: foo
To: bar
List-ID: Users of FOO <FOO-users.lists.example.COM>
Subject: baz

FOO IS TEH BEST
""",
        )
    cfg = ConfigParser.RawConfigParser()
    got = categorize.match_angle_bracket_header(
        cfg=cfg,
        depot=tmp,
        folder='mdir',
        path=os.path.join('new', '1196638757.V801Ia938aM515340.foo'),
        args=['List-id', 'Foo-Users.lists.EXAMPLE.COM'],
        )
    eq(got, dict())

def test_match_angle_bracket_header_nomatch():
    tmp = maketemp()
    maildir.create(os.path.join(tmp, 'mdir'))
    writeFile(
        os.path.join(tmp, 'mdir', 'new', '1196638757.V801Ia938aM515340.foo'),
        """\
From: bar
To: foo
List-ID: Users of BAR <BAR-users.lists.example.COM>
Subject: Re: baz

NO WE LIKES BAR MOAR
""",
        )
    cfg = ConfigParser.RawConfigParser()
    got = categorize.match_angle_bracket_header(
        cfg=cfg,
        depot=tmp,
        folder='mdir',
        path=os.path.join('new', '1196638757.V801Ia938aM515340.foo'),
        args=['List-id', 'Foo-Users.lists.EXAMPLE.COM'],
        )
    eq(got, None)

def test_match_all():
    tmp = maketemp()
    maildir.create(os.path.join(tmp, 'mdir'))
    writeFile(
        os.path.join(tmp, 'mdir', 'new', '1196638757.V801Ia938aM515340.foo'),
        'fake mail',
        )
    cfg = ConfigParser.RawConfigParser()
    got = categorize.match_all(
        cfg=cfg,
        depot=tmp,
        folder='mdir',
        path=os.path.join('new', '1196638757.V801Ia938aM515340.foo'),
        args=[],
        )
    eq(got, dict())
