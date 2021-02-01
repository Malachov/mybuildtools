"""
mypythontools
=============

Some tools - snippets used across projects.

Modules:
--------

build
-----
Build your app with pyinstaller just with calling one function `build_app`.
Check function doctrings for how to do it.

See module help for more informations.

githooks
--------

Some functions runned every each git action (usually before commit).

Can derive README.md from __init__.py or generate rst files necessary for sphinx docs generator.

Check module docstrings for how to use it.
"""

from . import githooks
from . import build

__version__ = "0.0.1"

__author__ = "Daniel Malachov"
__license__ = "MIT"
__email__ = "malachovd@seznam.cz"

__all__ = ['githooks', 'build']
