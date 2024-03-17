
Development
====================

The source of |managesieve| is maintained at
`GitLab <https://gitlab.com>`_.
Patches and pull-requests are hearty welcome.

* Please submit bugs and enhancements to the `Issue Tracker
  <https://gitlab.com/htgoebel/managesieve/issues>`_.

* You may browse the code at the
  `Repository Browser
  <https://gitlab.com/htgoebel/managesieve>`_
  Or you may check out the current version by running ::

    git clone https://gitlab.com/htgoebel/managesieve.git



*Historical Note:*
|managesieve| was hosted at origo.ethz.ch, which closed in May 2012.
Then |managesieve| was hosted on gitorious.org,
which was closed in May 2015 and merged into gitlab.


Set up Local Development Environment
-------------------------------------

The setup of a local development environment is pretty easy.
You only need `tox <https://tox.wiki/>`_,
which will manage the test and development requirements for you.
You can install `tox` via the
`recommended way <https://tox.wiki/en/latest/installation.html>`_
or simply by running :code:`pip install --user tox`.

* Running all tests and checks::

    tox

* Running only the code-checks::

    tox -e check

* Running only the tests::

    tox -e py

* Building the documentation locally::

    tox -e docs

  You will then find the documentation in :file:`_build/html`.


.. |managesieve| replace:: managesieve
