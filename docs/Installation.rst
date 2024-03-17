
Download & Installation
=========================

Instructions for Windows Users
-----------------------------------

1. |managesieve| requires Python. If you don't have Python installed
   already, download and install Python 3.12 from
   https://python.org/download/3.12/

   During installation, make sure to check "Include into PATH".

2. If you already have Python installed, please check that your Python
   directory (normally :file:`C:\Python312` for Python 3.12) and the Python
   Scripts directory (normally :file:`C:\Python312\Scripts`) are in the system
   path. If not, just add them in :menuselection:`My Computer --> Properties
   --> Advanced --> Environment Variables` to the :code:`Path` system
   variable.

3. Install `managesieve` by running ::

     pip install managesieve

   Then run the console command ``sieveshell --help`` to get detailed help.

   If the command ``pip`` is unknown to you system, please refer to the
   `pip installation instructions`_ for help.


Instructions for GNU/Linux and other Operating Systems
--------------------------------------------------------

Most current GNU/Linux distributions provide packages for Python.
Simply search your distribution's software catalog.

Also many other vendors provide Python, and some even provide |managesieve|.
Please check your vendor's software repository.

If your distribution or vendor does not provide a current version of
|managesieve| please read on.

If your vendor does not provide :command:`python`
please download Python 3.12 from https://www.python.org/download/ and
follow the installation instructions there.

If you distribution or vendor missed providing :command:`pip`,
alongside :command:`python`,
please check your vendor's or distribution's software repository
for a package called `pip` or `python-pip`.
If this is not provided, please refer to the
`pip installation instructions`_ for help.

Then continue with :ref:`installing managesieve` below.

.. _pip installation instructions:
       https://pip.pypa.io/en/stable/installing/

.. _installing managesieve:

Installing |managesieve| using :command:`pip`
---------------------------------------------

After installing `Python` just run::

  sudo pip install managesieve

to install |managesieve| for all users.
For installing |managesieve| for yourself only, run::

  pip install --user managesieve

If your system does not have network access
download |managesieve| from https://pypi.org/project/managesieve/, and
run ::

    sudo pip install managesieve-*.tar.gz

respective ::

    pip install --user managesieve-*.tar.gz


.. |managesieve| replace:: `managesieve`
