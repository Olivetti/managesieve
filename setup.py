#!/usr/bin/env python
# -*- ispell-local-dictionary: "american" -*-

"""Setup script for the managesieve"""

from setuptools import setup

description = "ManageSieve client library for remotely managing Sieve scripts"

setup (name = "managesieve",
       version = "0.5",
       description = description,
       long_description = open('README.txt').read().strip(),
       long_description_content_type = 'text/x-rst',
       author = "Hartmut Goebel",
       author_email = "h.goebel@crazy-compilers.com",
       #maintainer = "Hartmut Goebel",
       #maintainer_email = "h.goebel@crazy-compilers.com",
       url = "http://packages.python.org/managesieve",
       download_url = "http://pypi.python.org/pypi/managesieve",
       license = 'Python',
       platforms = ['POSIX'],
       keywords = ['sieve', 'managesieve', 'sieveshell', 'RFC 5804'],
       py_modules = ['managesieve'],
       scripts = ['sieveshell'],
       classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Python Software Foundation License',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Communications :: Email',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities'
          ],
     )
