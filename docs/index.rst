.. -*- mode: rst ; ispell-local-dictionary: "american" -*-

===============
`managesieve`
===============

-------------------------------------------------------------------------------------------------------------------------------------
A ManageSieve client library for remotely managing Sieve scripts, including an user application (the interactive 'sieveshell').
-------------------------------------------------------------------------------------------------------------------------------------

.. Contents:

.. toctree::
   :maxdepth: 2

   Installation
   Development
   modules
   Changes


:Author:  Hartmut Goebel <h.goebel@crazy-compiler.com>
:License: `Python Software Foundation License`__ for the module,
          `GPL v3`__ for `sieveshell` and test suite.
:Homepage: https://managesieve.readthedocs.io/
:Download: https://pypi.org/project/managesieve
:Development: https://gitlab.com/htgoebel/managesieve

__ http://www.opensource.org/licenses/PythonSoftFoundation.html
__ http://opensource.org/licenses/GPL-3.0

python-managesieve is a pure `Python <http://www.python.org/>`_ module
implementing the ManageSieve client protocol. It also includes an user
application (the interactive `sieveshell`).


What is this ManageSieve thing?
====================================

The ManageSieve protocol allows managing Sieve scripts on a remote
mail server. Sieve scripts allow users to filter incoming email on the
mail server. These servers are commonly sealed so users cannot log
into them, yet users must be able to update their scripts on them.
This is what for the "ManageSieve" protocol is. For more information
about the ManageSieve protocol see `the ManageSieve Internet draft
<http://www.ietf.org/internet-drafts/draft-martin-managesieve-07.txt>`_.

This module allows accessing a Sieve-Server for managing Sieve scripts
there. It is accompanied by a simple yet functional user application
`sieveshell`.

What is this `sieveshell`?
================================

`sieveshell` is a command line tool for talking to the Sieve server.
One can

* list scripts on the server
* upload scripts to the server
* display scripts stored on the server and download or edit them
* delete scripts stored on the server
* activate and deactivate scripts

`sieveshell` is useful for user who wish to manage sieve scripts
without installing a fat GUI-based mail client.


..
  Indices and tables
  ==================

  * :ref:`genindex`
  * :ref:`modindex`
  * :ref:`search`

