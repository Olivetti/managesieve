# -*- ispell-local-dictionary: "american" -*-
"""ManageSieve (RFC 5804) client module for remotely managing Sieve Scripts.


All Sieve commands are supported by methods of the same name (in
lower-case). All arguments to commands are converted to strings,
except for :meth:`authenticate`.

"""

__version__ = "0.6"
__author__ = """Hartmut Goebel <h.goebel@crazy-compilers.com>
Ulrich Eck <ueck@net-labs.de> April 2001
"""

__copyright__ = "Copyright (C) 2003-2018 by Hartmut Goebel <h.goebel@crazy-compilers.com> and others"
__license__ = "Python-2.0 like"

import binascii, re, socket, time, random, sys
import logging
from logging import log
try:
    import ssl
    ssl_wrap_socket = ssl.wrap_socket
except ImportError:
    ssl_wrap_socket = socket.ssl

# only used for assertion. TODO: Remove
try:
    unicode
except:
    unicode = str


__all__ = [ 'MANAGESIEVE', 'SIEVE_PORT', 'OK', 'NO', 'BYE',
            'INFO', 'DEBUG', 'DEBUG0', 'DEBUG1', 'DEBUG2', 'DEBUG3']

# logging levels
INFO = logging.INFO
DEBUG0 = DEBUG = logging.DEBUG+3 # commands and responses
DEBUG1 = logging.DEBUG+2 # send and read data (except long literals)
DEBUG2 = logging.DEBUG+1 # more details
DEBUG3 = logging.DEBUG   # all debug messages (pattern matching, etc.)

CRLF = b'\r\n'
SIEVE_PORT = 4190

OK = 'OK'
NO = 'NO'
BYE = 'BYE'

AUTH_PLAIN = "PLAIN"
AUTH_LOGIN = "LOGIN"
# authentication mechanisms currently supported
# in order of preference
AUTHMECHS = [AUTH_PLAIN, AUTH_LOGIN]

# todo: return results or raise exceptions?
# todo: on result 'BYE' quit immediatly
# todo: raise exception on 'BYE'?

#    Commands
commands = {
    # name            valid states
    b'STARTTLS':     ('NONAUTH',),
    b'AUTHENTICATE': ('NONAUTH',),
    b'LOGOUT':       ('NONAUTH', 'AUTH', 'LOGOUT'),
    b'CAPABILITY':   ('NONAUTH', 'AUTH'),
    b'GETSCRIPT':    ('AUTH', ),
    b'PUTSCRIPT':    ('AUTH', ),
    b'SETACTIVE':    ('AUTH', ),
    b'DELETESCRIPT': ('AUTH', ),
    b'LISTSCRIPTS':  ('AUTH', ),
    b'HAVESPACE':    ('AUTH', ),
    }

### needed
Oknobye = re.compile(r'(?P<type>(?:OK|NO|BYE))' # atom / ascii
                     r'(?: \((?P<code>.*)\))?'  # atom / ascii
                     r'(?: (?P<data>.*))?')     # string / utf-8
# draft-martin-managesieve-04.txt defines the size tag of literals to
# contain a '+' (plus sign) behind the digits, but timsieved does not
# send one. Thus we are less strikt here:
Literal = re.compile(r'.*{(?P<size>\d+)\+?}$')
re_dquote  = re.compile(r'"(([^"\\]|\\.)*)"')
re_esc_quote = re.compile(r'\\([\\"])')


class SSLFakeSocket:
    """A fake socket object that really wraps a SSLObject.

    It only supports what is needed in managesieve.
    """
    def __init__(self, realsock, sslobj):
        self.realsock = realsock
        self.sslobj = sslobj

    def send(self, str):
        self.sslobj.write(str)
        return len(str)

    sendall = send

    def close(self):
        self.realsock.close()

class SSLFakeFile:
    """A fake file like object that really wraps a SSLObject.

    It only supports what is needed in managesieve.
    """
    def __init__(self, sslobj):
        self.sslobj = sslobj

    def readline(self):
        str = b""
        chr = None
        while chr != b"\n":
            chr = self.sslobj.read(1)
            str += chr
        return str

    def read(self, size=0):
        if size == 0:
            return b''
        else:
            return self.sslobj.read(size)

    def close(self):
        pass


def sieve_name(name):
    """
    According to RFC 5804, sec 1.6 script names are UTF-8 encoded
    and must not contain
     -  0000-001F; [CONTROL CHARACTERS]
     -  007F; DELETE
     -  0080-009F; [CONTROL CHARACTERS]
     -  2028; LINE SEPARATOR
     - 2029; PARAGRAPH SEPARATOR
    """
    # todo: correct quoting
    return ('"%s"' % name).encode('utf-8')


def sieve_string(string):
    # utf-8 encoded literal
    octets = string.encode('utf-8')
    return ('{%d+}\r\n' % len(octets)).encode('ascii') + octets


class MANAGESIEVE:
    """Sieve client class.

    Instantiate with: MANAGESIEVE(host [, port])

    :param host: host's name (default: localhost)
    :param port: port number (default: standard Sieve port).
    :param use_tls:  switch to TLS automatically,
                     fail if the server doesn't support STARTTLS
    :param keyfile:  keyfile to use for TLS (optional)
    :param certfile: certfile to use for TLS (optional)
    """

    """
    However, the 'password' argument to the LOGIN command is always
    quoted. If you want to avoid having an argument string quoted (eg:
    the 'flags' argument to STORE) then enclose the string in
    parentheses (eg: "(\Deleted)").

    Errors raise the exception class <instance>.error("<reason>").
    IMAP4 server errors raise <instance>.abort("<reason>"),
    which is a sub-class of 'error'. Mailbox status changes
    from READ-WRITE to READ-ONLY raise the exception class
    <instance>.readonly("<reason>"), which is a sub-class of 'abort'.

    "error" exceptions imply a program error.
    "abort" exceptions imply the connection should be reset, and
            the command re-tried.
    "readonly" exceptions imply the command should be re-tried.

    Note: to use this module, you must read the RFCs pertaining
    to the IMAP4 protocol, as the semantics of the arguments to
    each IMAP4 command are left to the invoker, not to mention
    the results.
    """

    class error(Exception): """Logical errors - debug required"""
    class abort(error):     """Service errors - close and retry"""

    def __clear_knowledge(self):
        """clear/init any knowledge obtained from the server"""
        self.capabilities = []
        self.loginmechs = []
        self.implementation = ''
        self.supports_tls = 0

    def __init__(self, host='', port=SIEVE_PORT,
                 use_tls=False, keyfile=None, certfile=None):
        self.host = host
        self.port = port
        self.state = 'NONAUTH'

        self.response_text = self.response_code = None
        self.__clear_knowledge()

        # Open socket to server.
        self._open(host, port)

        if __debug__:
            self._cmd_log_len = 10
            self._cmd_log_idx = 0
            self._cmd_log = {}           # Last `_cmd_log_len' interactions
            self._log(INFO, 'managesieve version %s', __version__)

        # Get server welcome message,
        # request and store CAPABILITY response.
        typ, data = self._get_response()
        if typ == 'OK':
            self._parse_capabilities(data)
        if use_tls:
            if not self.supports_tls:
                self.abort('TLS requested, but server does not support TLS')
            typ, data = self.starttls(keyfile=keyfile, certfile=certfile)
            if typ == 'OK':
                self._parse_capabilities(data)


    def _parse_capabilities(self, lines):
        for line in lines:
            if len(line) == 2:
                typ, data = line
            else:
                assert len(line) == 1, 'Bad Capabilities line: %r' % line
                typ = line[0]
                data = None
            if __debug__:
                self._log(DEBUG0, '%s: %r', typ, data)
            if typ == "IMPLEMENTATION":
                self.implementation = data
            elif typ == "SASL":
                self.loginmechs = data.split()
            elif typ == "SIEVE":
                self.capabilities = data.split()
            elif typ == "STARTTLS":
                self.supports_tls = 1
            else:
                # A client implementation MUST ignore any other
                # capabilities given that it does not understand.
                pass
        return


    def __getattr__(self, attr):
        #    Allow UPPERCASE variants of MANAGESIEVE command methods.
        if attr in commands:
            return getattr(self, attr.lower())
        raise AttributeError("Unknown MANAGESIEVE command: '%s'" % attr)


    #### Private methods ###
    def _open(self, host, port):
        """Setup 'self.sock' and 'self.file'."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.file = self.sock.makefile('rb')

    def _close(self):
        self.file.close()
        self.sock.close()

    def _read(self, size):
        """Read 'size' bytes from remote."""
        data = b""
        while len(data) < size:
            data += self.file.read(size - len(data))
        return data

    def _readline(self):
        """Read line from remote."""
        # Continuation bytes are never 7-bit-ascii characters, so
        # using readline() scanning for CR and LR is okay here.
        line = self.file.readline()
        assert isinstance(line, bytes)
        line = line.decode('utf-8')
        assert isinstance(line, unicode)
        return line

    def _send(self, data):
        return self.sock.send(data)

    def _get_line(self):
        line = self._readline()
        if not line:
            raise self.abort('socket error: EOF')
        assert isinstance(line, unicode)
        # Protocol mandates all lines terminated by CRLF
        line = line[:-2]
        if __debug__:
            self._log(DEBUG1, '< %s', line)
        return line

    def _simple_command(self, *args):
        """Execute a command which does only return status.

        Returns (typ) with
           typ  = response type

        The response code and text may be found in :attr:`response_code`
        and :attr:`response_text`, respectivly.
        """
        return self._command(*args)[0] # only return typ, ignore data


    def _command(self, name, arg1=None, arg2=None, *options):
        """
        Returns (typ, data) with
           typ  = response type
           data = list of lists of strings read (only meaningfull if OK)

        The response code and text may be found in :attr:`.response_code`
        and :attr:`response_text`, respectivly.
        """
        assert isinstance(name, bytes)
        if self.state not in commands[name]:
            raise self.error(
                'Command %s illegal in state %s' % (name, self.state))
        # concatinate command and arguments (if any)
        data = b" ".join(filter(None, (name, arg1, arg2)))
        if __debug__:
            self._log(DEBUG1, '> %s', data)
        try:
            try:
                self._send(data + CRLF)
                for o in options:
                    if __debug__:
                        self._log(DEBUG1, '> %r', o)
                    self._send(o + CRLF)
            except (socket.error, OSError) as val:
                raise self.abort('socket error: %s' % val)
            return self._get_response()
        except self.abort as val:
            if __debug__:
                self._print_log()
            raise


    def _readstring(self, data):
        assert isinstance(data, unicode)
        if data.startswith(" ") : # space -> error
            raise self.error('Unexpected space: %r' % data)
        elif data.startswith('"'): # handle double quote:
            if not self._match(re_dquote, data):
                raise self.error('Unmatched quote: %r' % data)
            snippet = self.mo.group(1)
            return re_esc_quote.sub(br'\1', snippet), data[self.mo.end():]
        elif self._match(Literal, data):
            # read a 'literal' string
            size = int(self.mo.group('size'))
            if __debug__:
                self._log(DEBUG2, 'read literal size %s', size)
            return self._read(size).decode('utf-8'), self._get_line()
        else:
            data = data.split(' ', 1)
            if len(data) == 1:
                data.append('')
            return data

    def _get_response(self):
        """
        :returns: :tuple:(resp, data) with

           :resp: response (OK, NO, BYE)
           :data: list of lists of strings read (only meaningfull if OK)

        The response code and text may be found in :attr:`response_code`
        and :attr:`response_text`, respectivly.
        """

        """
    response-deletescript = response-oknobye
    response-authenticate = *(string CRLF) (response-oknobye)
    response-capability   = *(string [SP string] CRLF) response-oknobye
    response-listscripts  = *(string [SP "ACTIVE"] CRLF) response-oknobye
    response-oknobye      = ("OK" / "NO" / "BYE") [SP "(" resp-code ")"] [SP string] CRLF
    string                = quoted / literal
    quoted                = <"> *QUOTED-CHAR <">
    literal               = "{" number  "+}" CRLF *OCTET
                            ;; The number represents the number of octets
                            ;; MUST be literal-utf8 except for values

--> a response either starts with a quote-charakter, a left-bracket or
    OK, NO, BYE

"quoted" CRLF
"quoted" SP "quoted" CRLF
{size} CRLF *OCTETS CRLF
{size} CRLF *OCTETS CRLF
[A-Z-]+ CRLF

        """
        data = [] ; dat = None
        resp = self._get_line()
        assert isinstance(resp, unicode)
        while 1:
            if self._match(Oknobye, resp):
                typ, code, dat = self.mo.group('type','code','data')
                if __debug__:
                    self._log(DEBUG0, '%s response: %s %s', typ, code, dat)
                self.response_code = code
                self.response_text = None
                if dat:
                    self.response_text = self._readstring(dat)[0]

                # if server quits here, send code instead of empty data
                if typ == "BYE":
                    return typ, code
                return typ, data
            else:
                dat = []
                while 1:
                    dat1, resp = self._readstring(resp)
                    if __debug__:
                        self._log(DEBUG2, 'read: %r', dat1)
                        self._log(DEBUG3, 'rest: %r', resp)
                    dat.append(dat1)
                    if not resp.startswith(' '):
                        break
                    resp = resp[1:]
                if len(dat) == 1:
                    dat.append(None)
                data.append(dat)
                resp = self._get_line()
        return self.error('Should not come here')


    def _match(self, cre, s):
        # Run compiled regular expression match method on 's'.
        # Save result, return success.
        self.mo = cre.match(s)
        if __debug__ and self.mo is not None:
            self._log(DEBUG3, "\tmatched '%r' => %r", cre.pattern, self.mo.groups())
        return self.mo is not None


    if __debug__:

        def _log(self, level, msg, *args):
            if level == DEBUG1:
                # Keep log of last `_cmd_log_len' interactions for debugging.
                self._cmd_log[self._cmd_log_idx] = (msg, args)
                self._cmd_log_idx = (self._cmd_log_idx+1) % self._cmd_log_len
            log(level, msg, *args)
            
        def _print_log(self):
            idx, cnt = self._cmd_log_idx, len(self._cmd_log)
            log(logging.ERROR, 'last %d SIEVE interactions:', cnt)
            idx = idx % cnt
            while cnt:
                msg, args = self._cmd_log[idx]
                try:
                    log(logging.ERROR, msg, *args)
                except:
                    pass
                idx = (idx+1) % self._cmd_log_len
                cnt -= 1

    ### Public methods ###
    def authenticate(self, mechanism, *authobjects):
        """Authenticate to the server.

        :param str mechanism: authentication mechanism to use
        :param authobjects: authentication data for this mechanism

        :returns: response (:const:`OK`, :const:`NO`, :const:`BYE`)
        """
        # command-authenticate  = "AUTHENTICATE" SP auth-type [SP string]  *(CRLF string)
        # response-authenticate = *(string CRLF) (response-oknobye)
        mech = mechanism.upper()
        if not mech in self.loginmechs:
            raise self.error("Server doesn't allow %s authentication." % mech)

        authobjects = [ao.encode('utf-8') for ao in authobjects]
        if mech == AUTH_LOGIN:
            authobjects = [ sieve_name(binascii.b2a_base64(ao)[:-1].decode('ascii'))
                            for ao in authobjects
                            ]
        elif mech == AUTH_PLAIN:
            if len(authobjects) < 3:
                # assume authorization identity (authzid) is missing
                # and these two authobjects are username and password
                authobjects.insert(0, b'')
            ao = b'\0'.join(authobjects)
            ao = binascii.b2a_base64(ao)[:-1].decode('ascii')
            authobjects = [ sieve_string(ao) ]
        else:
            raise self.error("managesieve doesn't support %s authentication." % mech)

        typ, data = self._command(b'AUTHENTICATE',
                                  sieve_name(mech), *authobjects)
        if typ == 'OK':
            self.state = 'AUTH'
        return typ


    def login(self, auth, user, password):
        """
        Authenticate to the Sieve server using the best mechanism available.

        :returns: response (:const:`OK`, :const:`NO`, :const:`BYE`)
        """
        for authmech in AUTHMECHS:
            if authmech in self.loginmechs:
                authobjs = [auth, user, password]
                if authmech == AUTH_LOGIN:
                    authobjs = [user, password]
                return self.authenticate(authmech, *authobjs)
        else:
            raise self.abort('No matching authentication mechanism found.')

    def logout(self):
        """Terminate connection to server.

        :returns: response (:const:`OK`, :const:`NO`, :const:`BYE`)
        """
        # command-logout        = "LOGOUT" CRLF
        # response-logout       = response-oknobye
        typ = self._simple_command(b'LOGOUT')
        self.state = 'LOGOUT'
        self._close()
        return typ


    def listscripts(self):
        """Get a list of scripts on the server.

        :returns: tuple(response, [data]) --
                  if `response` is :const:`OK`, `data` is a list of
                  `(scriptname, active)` tuples.
        """
        # command-listscripts   = "LISTSCRIPTS" CRLF
        # response-listscripts  = *(sieve-name [SP "ACTIVE"] CRLF) response-oknobye
        typ, data = self._command(b'LISTSCRIPTS')
        if typ != 'OK': return typ, data
        scripts = []
        for dat in data:
            if __debug__:
                if not len(dat) in (1, 2):
                    self.error("Unexpected result from LISTSCRIPTS: %r" (dat,))
            scripts.append( (dat[0], dat[1] is not None ))
        return typ, scripts


    def getscript(self, scriptname):
        """Get a script from the server.

        :param str scriptname: name of script to be retrieved

        :returns: tuple(response, str) --
                  if `response` is :const:`OK`, `str` is the script content.
        """
        # command-getscript     = "GETSCRIPT" SP sieve-name CRLF
        # response-getscript    = [string CRLF] response-oknobye
        
        typ, data = self._command(b'GETSCRIPT', sieve_name(scriptname))
        if typ != 'OK': return typ, data
        if len(data) != 1:
            self.error('GETSCRIPT returned more than one string/script')
        # todo: decode data?
        return typ, data[0][0]
    

    def putscript(self, scriptname, scriptdata):
        """Put a script onto the server.

        :param str scriptname: name of script to be retrieved
        :param str scriptdata: script content

        :returns: response (:const:`OK`, :const:`NO`, :const:`BYE`)
        """
        # command-putscript     = "PUTSCRIPT" SP sieve-name SP string CRLF
        # response-putscript    = response-oknobye
        return self._simple_command(b'PUTSCRIPT',
                                    sieve_name(scriptname),
                                    sieve_string(scriptdata)
                                    )

    def deletescript(self, scriptname):
        """Delete a scripts at the server.

        :param str scriptname: name of script to be deleted

        :returns: response (:const:`OK`, :const:`NO`, :const:`BYE`)
        """
        # command-deletescript  = "DELETESCRIPT" SP sieve-name CRLF
        # response-deletescript = response-oknobye
        return self._simple_command(b'DELETESCRIPT', sieve_name(scriptname))


    def setactive(self, scriptname):
        """Mark a script as the 'active' one.

        :param str scriptname: name of script to be marked active

        :returns: response (:const:`OK`, :const:`NO`, :const:`BYE`)
        """
        # command-setactive     = "SETACTIVE" SP sieve-name CRLF
        # response-setactive    = response-oknobye
        return self._simple_command(b'SETACTIVE', sieve_name(scriptname))


    def havespace(self, scriptname, size):
        """Query the server for available space.

        :param str scriptname: name of script to XXX
        :param int size: XXX

        :returns: response (:const:`OK`, :const:`NO`, :const:`BYE`)
        """
        # command-havespace     = "HAVESPACE" SP sieve-name SP number CRLF
        # response-havespace    = response-oknobye
        return self._simple_command(b'HAVESPACE',
                                    sieve_name(scriptname),
                                    str(size).encode('ascii'))


    def capability(self):
        """
        Issue a CAPABILITY command and return the result.
        
        As a side-effect, on succes these attributes are (re)set:

        - :attr:`capabilities` (list of strings)
        - :attr:`loginmechs` (list of strings)
        - :attr:`implementation` (string)
        - :attr:`supports_tls` (boolean)

        :returns: tuple(response, capabilities) --
                  If `response` is :const:`OK`, `capabilities` is a list
                  of strings.
        """
        # command-capability    = "CAPABILITY" CRLF
        # response-capability   = *(string [SP string] CRLF) response-oknobye
        typ, data = self._command(b'CAPABILITY')
        if typ == 'OK':
            self._parse_capabilities(data)
        return typ, data


    def starttls(self, keyfile=None, certfile=None):
        """Puts the connection to the SIEVE server into TLS mode.

        If the server supports TLS, this will encrypt the rest of the SIEVE
        session. If you provide the keyfile and certfile parameters,
        the identity of the SIEVE server and client can be checked. This,
        however, depends on whether the socket module really checks the
        certificates.
        """
        # command-starttls      = "STARTTLS" CRLF
        # response-starttls     = response-oknobye
        typ, data = self._command(b'STARTTLS')
        if typ == 'OK':
            sslobj = ssl_wrap_socket(self.sock, keyfile, certfile)
            self.sock = SSLFakeSocket(self.sock, sslobj)
            self.file = SSLFakeFile(sslobj)
            # MUST discard knowledge obtained from the server
            self.__clear_knowledge()
            # NB: We did send a BOGUS command here for buggy servers,
            # but RFC 5804 forbids doing this. And it broke with
            # servers following the RFC.
            typ, data = self._get_response()
            # Buggy servers may not advertise capabilities, thus we
            # need to ask.
            self.capability()
            if __debug__:
                self._log(INFO, 'started Transport Layer Security (TLS)')
        return typ, data
