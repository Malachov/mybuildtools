""" Test module. Auto pytest that can be started in IDE or with

    >>> python -m pytest

in terminal in tests folder.
"""
#%%

from pathlib import Path
import os
import inspect
import shutil
import sys

# Find paths and add to sys.path to be able to import local modules
test_path = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parent
root_path = test_path.parent

if root_path not in sys.path:
    sys.path.insert(0, root_path.as_posix())

import mypythontools


def test_it():

    shutil.rmtree(root_path / 'build', ignore_errors=True)
    if (root_path / 'docs' / 'source' / 'modules.rst').exists():
        (root_path / 'docs' / 'source' / 'modules.rst').unlink()  # missing_ok=True from python 3.8 on...

    mypythontools.utils.generate_readme_from_init(git_add=False)
    mypythontools.utils.sphinx_docs_regenerate(git_add=False)
    mypythontools.utils.get_version()

    # TODO test if correct

    # Build app with pyinstaller example
    mypythontools.misc.set_paths(set_root_path=test_path)
    mypythontools.build.build_app(main_file='app.py', console=True, debug=True, cleanit=False)
    mypythontools.misc.set_paths()

    passed = (test_path / 'dist').exists() and (root_path / 'docs' / 'source' / 'modules.rst').exists()

    shutil.rmtree(root_path / 'tests' / 'build')
    shutil.rmtree(root_path / 'tests' / 'dist')

    assert passed
