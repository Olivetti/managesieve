#!/usr/bin/env python
# -*- ispell-local-dictionary: "american" -*-

"""Setup script for the managesieve"""

from setuptools import setup

description = "ManageSieve client library for remotely managing Sieve scripts"

# Read the contents of the README file
from os import path
import io
this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, 'README.txt'), encoding='utf-8') as f:
    long_description = f.read()

setup (name = "managesieve",
       version='0.6',
       python_requires='>=2.7',
       setup_requires=["pytest-runner"],
       tests_require=["pytest"],
       description = description,
       long_description = long_description,
       long_description_content_type = 'text/x-rst',
       author = "Hartmut Goebel",
       author_email = "h.goebel@crazy-compilers.com",
       #maintainer = "Hartmut Goebel",
       #maintainer_email = "h.goebel@crazy-compilers.com",
       url = "https://managesieve.readthedocs.io/",
       download_url = "https://pypi.org/project/managesieve",
       project_urls={
           'Documentation': 'https://managesieve.readthedocs.io/',
           'Source Code': 'https://gitlab.com/htgoebel/managesieve/',
           "Bug Tracker": "https://gitlab.com/htgoebel/managesieve/issues",
           'Funding': 'http://crazy-compilers.com/donate.html',
       },
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
