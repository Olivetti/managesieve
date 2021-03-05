#!/usr/bin/env python
"""
Unit tests for managesieve.py
"""

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "(c) Copyright 2003-2021 by Hartmut Goebel"
__license__ = "GNU General Public License, version 3"

import io

import pytest

import managesieve


try:
    unicode
except:
    unicode = str


def make_string(string):
    assert isinstance(string, str)
    # According to RFC 5804, sec 1.4 all strings are UTF-8 encoded
    octets = string.encode('utf-8')
    return b''.join((('{%d+}' % len(octets)).encode('ascii'),
                     CRLF, octets))

def cmd_str(*args):
    args = [a.encode('utf-8') if isinstance(a, unicode) else a
            for a in args]
    return b' '.join(args)

def __makeResponses(responseTuples):
    """
    Yield elements of tuples
       (exp_res, exp_code, exp_text, send_bytes)
    All elements are bytes since they are used for
    """
    for res, entries in responseTuples.items():
        for code, text in entries:
            # this in ineffizient, but simple code which is more
            # important for testing
            code1 = ('(%s)' % code).encode('utf-8') if code else None
            text1 = ('"%s"' % text).encode('utf-8') if text else None
            text2 = make_string(text) if text else None
            res_ = res.encode('utf-8')
            code_ = code.encode('utf-8') if code else None
            text_ = text.encode('utf-8') if text else None
            if code and text:
                # '%s %s "%s"' % (res, code, text)
                # '%s %s %s'   % (res, code, make_string(text))
                yield res, code, text, b' '.join((res_, code1, text1)) + CRLF
                yield res, code, text, b' '.join((res_, code1, text2)) + CRLF
            elif text:
                # %s "%s"' % (res, text)
                # '%s %s'   % (res, make_string(text))
                yield res, code, text, b' '.join((res_, text1)) + CRLF
                yield res, code, text, b' '.join((res_, text2)) + CRLF
            elif code:
                yield res, code, text, b' '.join((res_, code1)) + CRLF
            else:
                yield res, code, text, res_ + CRLF

CRLF = b'\r\n'
OK = 'OK' ; NO = 'NO' ; BYE = 'BYE' # just for ease typing :-)

SieveNames = 'sieve-name1 another_sieve_name'.split()
Scripts = [
    ( 'keep ;') ,
    ( 'if header :contains "Subject" "Test ignore" {'
      '    reject ;'
      '}'),
    ]

ListScripts = [('"%s"' % s).encode('utf-8') for s in SieveNames] + \
              [make_string(s) for s in SieveNames]
Script_List = [ (s, False) for s in  SieveNames ] * 2
ListScripts[2] = ListScripts[2] + b" ACTIVE" # set one active
Script_List[2] = (Script_List[2][0], True)  # set one active
ListScripts = CRLF.join(ListScripts)
print(ListScripts)
print(Script_List)

RESP_OKAY      = 'Okay.'
RESP_CODE_OKAY = 'RESP-OKAY/ALL'

RESP_FAIL      = 'Failed.'
RESP_CODE_FAIL = 'RESP-FAIL/ALL'

RESP_TIMEOUT       = 'Connection timed out.'
RESP_CODE_TIMEOUT  = 'RESP-BYE/TIMEOUT'

ResponseTuples = {
    OK:  [ (None,           None),
           (None,           RESP_OKAY),
           (RESP_CODE_OKAY, None),
           (RESP_CODE_OKAY, RESP_OKAY),
           ],
    NO:  [ (None,           None),
           (None,           RESP_FAIL),
           (RESP_CODE_FAIL, None),
           (RESP_CODE_FAIL, RESP_FAIL),
           ],
    BYE: [ (None,              None),
           (None,              RESP_TIMEOUT),
           (RESP_CODE_TIMEOUT, None),
           (RESP_CODE_TIMEOUT, RESP_TIMEOUT),
           ]
    }

Responses = list(__makeResponses(ResponseTuples))
print(Responses)

class SIEVEforTest(managesieve.MANAGESIEVE):
    def __init__(self, response_data=None):
        if response_data is None:
            response_data = Responses[0][-1]
        self._set_response_data(response_data)
        managesieve.MANAGESIEVE.__init__(self)
        #self.state = 'AUTH'

    def _open(self, host, port):
        # cmd_file : the buffer where the command is send to
        self.cmd_file = io.BytesIO()
        # resp_file: the buffer where the response is read from
        # this will be set up in __set_testdata()
        #self.file = self.resp_file = None

    def _close(self):
        pass

    def _send(self, data):
        return self.cmd_file.write(data)

    def xx_get_response(self):
        # a wrapper arround managesieve.SIEVE._get_response()
        self.cmd_file.truncate()
        self.cmd_file.seek(0)
        result = managesieve.SIEVE._get_response(self)
        self.resp_file.truncate()
        self.resp_file.seek(0)
        return result

    def _set_response_data(self, response):
        self.file = self.resp_file = io.BytesIO(response)

    def _get_command_data(self):
        self.cmd_file.truncate()
        self.cmd_file.seek(0)
        return self.cmd_file.getvalue()


@pytest.fixture
def testSieve():
    sieve = SIEVEforTest()
    sieve.state = 'AUTH'
    return sieve


def _test_simple(testSieve, exp_res, exp_code, exp_text, send_cmd,
                 exp_cmd_str, func, *args):
    testSieve._set_response_data(send_cmd)
    result = func(*args)
    # check if the correct command data has be send
    assert testSieve._get_command_data() == (exp_cmd_str + CRLF)
    # check if we've recieved the expected response and data
    assert result == exp_res
    assert testSieve.response_code == exp_code
    assert testSieve.response_text == exp_text


def _test_with_responce_data(testSieve,
            exp_res, exp_code, exp_text, send_cmd,
            send_data, exp_data,
            exp_cmd_str,func, *args):
    testSieve._set_response_data(send_data + CRLF + send_cmd)
    result, data = func(*args)
    # check if the correct command data has be send
    assert testSieve._get_command_data() == (exp_cmd_str + CRLF)
    # check if we've recieved the expected response and data
    assert result == exp_res
    assert testSieve.response_code == exp_code
    assert testSieve.response_text == exp_text
    # check if we've recieved the expected data
    if result == OK:
        assert data == exp_data


#--- basic functions ---

def test_init():
    sieve = SIEVEforTest(
        b'"IMPLEMENTATION" "Cyrus timsieved 2.4.17"\r\n'
        b'"SASL" "DIGEST-MD5 NTLM LOGIN PLAIN"\r\n'
        b'"SIEVE" "comparator-i;ascii-numeric fileinto subaddress copy"\r\n'
        b'"STARTTLS"\r\n'
        b'"UNAUTHENTICATE"\r\n'
        b'OK\r\n')
    assert sieve.supports_tls
    assert set(sieve.loginmechs) == set("DIGEST-MD5 NTLM LOGIN PLAIN".split())
    assert set(sieve.capabilities) == set("comparator-i;ascii-numeric fileinto subaddress copy".split())

def test_init_wring_data():
    with pytest.raises(SIEVEforTest.error):
        sieve = SIEVEforTest(
            b' "IMPLEMENTATION" "Cyrus timsieved 2.4.17"\r\n'
            b'OK\r\n')

def test__command():
    sn = managesieve.sieve_name
    sieve = SIEVEforTest(
        b'OK\r\n'
        b'OK\r\n')
    sieve._command(b'STARTTLS', sn("arg1"), sn("arg2"),
                   b"arg3", b"arg4", b"arg5", b"arg6")

def test_authenticate_plain1():
    sieve = SIEVEforTest(
        b'"SASL" "LOGIN PLAIN"\r\n'
        b'OK\r\n'
        b'OK\r\n')
    sieve.authenticate('PLAIN', "myname", "mypassword")
    assert sieve.state == 'AUTH'

def test_authenticate_plain2():
    sieve = SIEVEforTest(
        b'"SASL" "LOGIN PLAIN"\r\n'
        b'OK\r\n'
        b'OK\r\n')
    sieve.authenticate('PLAIN', "myname", "myname", "mypassword")
    assert sieve.state == 'AUTH'

def test_authenticate_login():
    sieve = SIEVEforTest(
        b'"SASL" "LOGIN PLAIN"\r\n'
        b'OK\r\n'
        b'OK\r\n')
    sieve.authenticate('LOGIN', "myauth", "myname", "mypassword")
    assert sieve.state == 'AUTH'

#--- simple commands ---

@pytest.mark.parametrize("exp_res, exp_code, exp_text, send_cmd", Responses)
def test_Logout(testSieve, exp_res, exp_code, exp_text, send_cmd):
    _test_simple(testSieve, exp_res, exp_code, exp_text, send_cmd,
        cmd_str('LOGOUT'),
        testSieve.logout)
    assert testSieve.state == 'LOGOUT'
    testSieve.state = 'AUTH'


@pytest.mark.parametrize("exp_res, exp_code, exp_text, send_cmd", Responses)
def testSimpleCommands1(testSieve, exp_res, exp_code, exp_text, send_cmd):
    _test_simple(testSieve, exp_res, exp_code, exp_text, send_cmd,
        cmd_str('DELETESCRIPT', '"%s"' % SieveNames[0]),
        testSieve.deletescript, SieveNames[0])


@pytest.mark.parametrize("exp_res, exp_code, exp_text, send_cmd", Responses)
def testSimpleCommands2(testSieve, exp_res, exp_code, exp_text, send_cmd):
    _test_simple(testSieve, exp_res, exp_code, exp_text, send_cmd,
        cmd_str('HAVESPACE', '"%s"' % SieveNames[0], '9999'),
        testSieve.havespace, SieveNames[0], 9999)


@pytest.mark.parametrize("exp_res, exp_code, exp_text, send_cmd", Responses)
def testListScripts(testSieve, exp_res, exp_code, exp_text, send_cmd):
    _test_with_responce_data(testSieve, exp_res, exp_code, exp_text, send_cmd,
        ListScripts, Script_List,
        cmd_str('LISTSCRIPTS'),
        testSieve.listscripts)
        

@pytest.mark.parametrize("exp_res, exp_code, exp_text, send_cmd", Responses)
def testGetscript(testSieve, exp_res, exp_code, exp_text, send_cmd):
    for s in Scripts:
        _test_with_responce_data(testSieve, exp_res, exp_code, exp_text, send_cmd,
            make_string(s), s,
            cmd_str('GETSCRIPT', '"%s"' % SieveNames[0]),
            testSieve.getscript, SieveNames[0])


@pytest.mark.parametrize("exp_res, exp_code, exp_text, send_cmd", Responses)
def testPutscript(testSieve, exp_res, exp_code, exp_text, send_cmd):
    for s in Scripts:
        _test_simple(testSieve, exp_res, exp_code, exp_text, send_cmd,
            cmd_str('PUTSCRIPT', '"%s"' % SieveNames[0], make_string(s)),
            testSieve.putscript, SieveNames[0], s)
