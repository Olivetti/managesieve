#!/usr/bin/env python
# -*- ispell-local-dictionary: "american" -*-

"""Setup script for the managesieve"""

from setuptools import setup

description = "ManageSieve client library for remotely managing Sieve scripts"

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
import sys
if sys.version_info < (2,2,3):
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

install_requires = []
if sys.version_info < (2,3):
    install_requires.append('logging')

setup (name = "managesieve",
       version = "0.5",
       description = description,
       long_description = open('README.txt').read().strip(),
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
       install_requires = install_requires,
       classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Python Software Foundation License',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Communications :: Email',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities'
          ],
     )
