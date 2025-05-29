===============
`managesieve`
===============

---------------------------------------------------------------------------------------------------------------------------------------
RFC-5804 Manage Sieve client library for remotely managing Sieve scripts, including an user application (the interactive 'sieveshell').
---------------------------------------------------------------------------------------------------------------------------------------

:Author:      Hartmut Goebel <h.goebel@crazy-compilers.com>
:Version:     0.8.1
:Copyright:   2003-2024 by Hartmut Goebel
:Licence:     Python Software Foundation License and
              GNU Public Licence v3 (GPLv3)
:Homepage:    https://managesieve.readthedocs.io/
:Development: https://gitlab.com/htgoebel/managesieve

Sieve scripts allow users to filter incoming email on the mail server.
The ManageSieve protocol allows managing Sieve scripts on a remote
mail server. These servers are commonly sealed so users cannot log
into them, yet users must be able to update their scripts on them.
This is what for the "ManageSieve" protocol is. For more information
about the ManageSieve protocol see `RFC 5804
<https://datatracker.ietf.org/doc/html/rfc5804>`_.

This module allows accessing a Sieve-Server for managing Sieve scripts
there. It is accompanied by a simple yet functional user application
'sieveshell'.


Changes since 0.7
~~~~~~~~~~~~~~~~~~~~~

* Now supports Python 3.6 to 3.13.

:managesieve:
   - Add support for the UNAUTHENTICATE command.
   - Add a socket timeout parameter.
   - Add support for IPv6.
   - Allow disabling certificate verification.
   - Follow the 'Logging for a Library' guideline.
   - BREAKING: Rearrange DEBUG logging levels to be more reasonable.
     See `docs/Logging.rst` for details.

:sieveshell:
   - Add option '--no-tls-verify'.
   - Improve error message if TLS certificate verification fails.
   - Keep line-endings on file IO.
   - Remove temporary file on successful edit, too.
   - Fix: Pass to sieve.login() the Authorization ID

:general:
   - Add support for Python 3.12.
   - Improve testing, add a tox.ini file and add CI/CD.
   - Fix SPDX license identifier.
   - Fix several typos.
   - Lint all the code.
   - Remove unused code.


Requirements and Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`managesieve` requires

* `Python`__ 3.6—3.12 and
* `pip`__ for installation.

__ https://www.python.org/download/
__ https://pypi.org/project/pip


Not yet implemented
~~~~~~~~~~~~~~~~~~~~~~~~

- sieve-names are only quoted dump (put into quotes, but no escapes yet).


Copyright and License
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: © 2003-2024 by Hartmut Goebel <h.goebel@crazy-compilers.com>

:License for `managesieve`:
   PSF-like License, see enclosed file

:License for 'sieveshell' and test suite: `GPL v3
   <https://opensource.org/licenses/GPL-3.0>`_


Credits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on Sieve.py from Ulrich Eck <ueck@net-labs.de> which is part of
of `ImapClient`__ , a Zope product.

__ https://web.archive.org/web/20050309230135/http://www.zope.org/Members/jack-e/ImapClient


Some ideas taken from imaplib written by Piers Lauder
<piers@cs.su.oz.au> et al.

Thanks to Tomas 'Skitta' Lindroos, Lorenzo Boccaccia, Alain Spineux,
darkness, Gregory Boyce and Grégoire Détrez for sending patches.

.. Emacs config:
 Local Variables:
 mode: rst
 End:
