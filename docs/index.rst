.. -*- mode: rst ; ispell-local-dictionary: "american" -*-

===============
`managesieve`
===============

.. highlights::

   A pure Python application (the interactive `sieveshell`) for
   remotely managing Sieve scripts. For developers it includes a
   Python module implementing the ManageSieve client protocol
   (:rfc:`5804`).

.. Contents:

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: User Documentation

   Installation
   Dontate <Donate>
   Changes

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Developer Documentation

   Development
   modules



:Author:  Hartmut Goebel <h.goebel@crazy-compiler.com>
:License: `Python Software Foundation License`__ for the module,
          `GPL v3`__ for `sieveshell` and test suite.
:Homepage: https://managesieve.readthedocs.io/
:Download: https://pypi.org/project/managesieve
:Development: https://gitlab.com/htgoebel/managesieve

__ http://www.opensource.org/licenses/PythonSoftFoundation.html
__ http://opensource.org/licenses/GPL-3.0


What is the `sieveshell`?
================================

`sieveshell` is a command line tool for talking to a remote
mail server. Sieve scripts allow users to filter incoming email on the
mail server.
Typically these servers are sealed so users cannot log
into them, yet users must be able to update their scripts on them.
This is what `sieveshell` is for.

One can

* list scripts on the server
* upload scripts to the server
* display scripts stored on the server and download or edit them
* delete scripts stored on the server
* activate and deactivate scripts

`sieveshell` is simple yet functional and
useful for user who wish to manage sieve scripts
without installing a fat GUI-based mail client.


What is managesieve?
====================================

The |managesieve| pure Python module is
a ManageSieve (:rfc:`5804`) client library
for managing Sieve scripts on a mail server,
more specific the `Sieve` server.
For API details see the :ref:`Module Documentation`.


..
  Indices and tables
  ==================

  * :ref:`genindex`
  * :ref:`modindex`
  * :ref:`search`


.. include:: _common_definitions.txt
