"""
This module can be used for example in running deploy pipelines or githooks
(some code automatically executed before commit). This module can run the tests,
edit library version, generate rst files for docs, push to git or deploy app to pypi.

All of that can be done with one function call - with `push_pipeline` function that
run other functions, or you can use functions separately. If you are using other
function than `push_pipeline`, you need to call `mypythontools.paths.set_paths()` first.


Examples:
=========

    **VS Code Task example**

    You can push changes with single click with all the hooks displaying results in
    your terminal. All params changing every push (like git message or tag) can
    be configured on the beginning and therefore you don't need to wait for test finish.
    Default values can be also used, so in small starting projects, push is actually very fast.

    Create folder utils, create push_script.py inside, add

    >>> import mypythontools
    ...
    >>> if __name__ == "__main__":
    ...     mypythontools.utils.push_pipeline(deploy=True)  # With all the params you need.

    Then just add this task to global tasks.json::

        {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Hooks & push & deploy",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "${workspaceFolder}/utils/push_script.py",
                        "--commit_message",
                        "${input:git-message}",
                        "--tag",
                        "${input:git-tag}",
                        "--tag_mesage",
                        "${input:git-tag-message}"
                    ],
                    "presentation": {
                        "reveal": "always",
                        "panel": "new"
                    }
                }
            ],
            "inputs": [
                {
                    "type": "promptString",
                    "id": "git-message",
                    "description": "Git message for commit.",
                    "default": "New commit"
                },
                {
                    "type": "promptString",
                    "id": "git-tag",
                    "description": "Git tag.",
                    "default": "__version__"
                },
                {
                    "type": "promptString",
                    "id": "git-tag-message",
                    "description": "Git tag message.",
                    "default": "New version"
                }
            ]
        }

    **Git hooks example**

    Create folder git_hooks with git hook file - for prec commit name must be `pre-commit`
    (with no extension). Hooks in git folder are gitignored by default (and hooks is not visible
    on first sight).

    Then add hook to git settings - run in terminal (last arg is path (created folder))::

        $ git config core.hooksPath git_hooks

    In created folder on first two lines copy this::

        #!/usr/bin/env python
        # -*- coding: UTF-8 -*-

    Then just import any function from here and call with desired params. E.g.

    >>> import mypythontools
    >>> mypythontools.paths.set_paths()
    >>> mypythontools.utils.run_tests()
    ============================= test session starts =============================
    ...
    >>> mypythontools.utils.set_version('increment')
"""

import argparse
import ast
import importlib
from pathlib import Path
import subprocess

import mylogging

from . import paths
from . import deploy as deploy_module

# Lazy loaded
# from git import Repo


def push_pipeline(
    tests=True,
    version="increment",
    sphinx_docs=True,
    git_params={
        "commit_message": "New commit",
        "tag": "__version__",
        "tag_mesage": "New version",
    },
    deploy=False,
):
    """Run pipeline for pushing and deploying app. Can run tests, generate rst files for sphinx docs,
    push to github and deploy to pypi. git_params can be configured not only with function params,
    but also from command line with params and therefore callable from terminal and optimal to run
    from IDE (for example with creating simple VS Code task).

    Check utils module docs for implementation example.

    Args:
        tests (bool, optional): Whether run pytest tests. Defaults to True.
        version (str, optional): New version. E.g. '1.2.5'. If 'increment', than it's auto incremented.
            If None, then version is not changed. 'Defaults to "increment".
        sphinx_docs((bool, list), optional): Whether generate sphinx apidoc and generate rst files for documentation.
            Some files in docs source can be deleted - check `sphinx_docs` docstrings for details and insert
            `exclude_paths` list if have some extra files other than ['conf.py', 'index.rst', '_static', '_templates'].
            Defaults to True.
        git_params (dict, optional): Git message, tag and tag mesage. If empty dict - {},
            than files are not git pushed. If tag is '__version__', than is automatically generated
            from __init__ version. E.g from '1.0.2' to 'v1.0.2'.
            Defaults to { 'commit_message': 'New commit', 'tag': '__version__', 'tag_mesage': 'New version' }.
        deploy (bool, optional): Whether deploy to PYPI. Defaults to False.

    Example:
        Recommended use is from IDE (for example with Tasks in VS Code). Check utils docs for how to use it.
        You can also use it from python...

        >>> import mypythontools
        ...
        >>> if __name__ == "__main__":
        ...     mypythontools.utils.push_pipeline(deploy=True)  # With all the params you need.

    """

    if not all([paths.ROOT_PATH, paths.APP_PATH, paths.INIT_PATH]):
        paths.set_paths()

    if tests:
        run_tests()

    if version:
        set_version(version)

    if isinstance(sphinx_docs, list):
        sphinx_docs_regenerate(exclude_paths=sphinx_docs)
    elif sphinx_docs:
        sphinx_docs_regenerate()

    if git_params:
        parser = argparse.ArgumentParser(description="Prediction framework setting via command line parser!")

        parser.add_argument(
            "--commit_message",
            type=str,
            help="Commit message. Defaults to: 'New commit'",
        )
        parser.add_argument(
            "--tag",
            type=str,
            help="Tag. E.g 'v1.1.2'. If '__version__', get the version. Defaults to: '__version__'",
        ),
        parser.add_argument("--tag_mesage", type=str, help="Tag message. Defaults to: 'New version'"),

        parser_args_dict = {k: v for k, v in parser.parse_known_args()[0].__dict__.items() if v is not None}

        if parser_args_dict:
            git_params.update(parser_args_dict)

        git_push(
            commit_message=git_params["commit_message"],
            tag=git_params["tag"],
            tag_message=git_params["tag_mesage"],
        )

    if deploy:
        deploy_module.deploy_to_pypi()


def git_push(commit_message, tag="__version__", tag_message="New version"):
    """Stage all changes, commit, add tag and push. If tag = '__version__', than tag
    is infered from __init__.py.

    Args:
        commit_message (str): Commit message.
        tag (str, optional): Define tag used in push. If tag is '__version__', than is automatically generated
            from __init__ version. E.g from '1.0.2' to 'v1.0.2'.  Defaults to '__version__'.
        tag_message (str, optional): Message in anotated tag. Defaults to 'New version'.
    """

    from git import Repo

    git_add_command = "git add . "

    subprocess.run(git_add_command.split(), shell=True, check=True, cwd=paths.ROOT_PATH)

    subprocess.run(
        ["git", "commit", "-m", commit_message],
        shell=True,
        check=True,
        cwd=paths.ROOT_PATH,
    )

    if not tag_message:
        tag_message = "New version"

    if tag == "__version__":
        tag = f"v{get_version()}"

    Repo(paths.ROOT_PATH).create_tag(tag, message=tag_message)

    git_push_command = "git push --follow-tags"

    subprocess.run(git_push_command, shell=True, check=True, cwd=paths.ROOT_PATH)


def set_version(version="increment"):
    """Change your version in your __init__.py file.


    Args:
        version (str, optional): If version is 'increment', it will increment your __version__
            in you __init__.py by 0.0.1. Defaults to "increment".

    Raises:
        ValueError: If no __version__ is find. Try set INIT_PATH via paths.set_paths...
    """

    with open(paths.INIT_PATH, "r") as init_file:

        list_of_lines = init_file.readlines()

        for i, j in enumerate(list_of_lines):
            if j.startswith("__version__"):

                delimiter = '"' if '"' in j else "'"
                delimited = j.split(delimiter)

                if version == "increment":
                    version_list = delimited[1].split(".")
                    version_list[2] = str(int(version_list[2]) + 1)
                    delimited[1] = ".".join(version_list)

                else:
                    delimited[1] = version

                list_of_lines[i] = delimiter.join(delimited)
                break

        else:
            raise ValueError(
                mylogging.return_str("__version__ variable not found in __init__.py. Try set INIT_PATH.")
            )

    with open(paths.INIT_PATH, "w") as init_file:

        init_file.writelines(list_of_lines)


def get_version(INIT_PATH=None):
    """Get version info from __init__.py file.

    Args:
        INIT_PATH ((str, Path), optional): Path to __init__.py file. If None, it's taken from paths module
            if used paths.set_paths() before. Defaults to None.

    Returns:
        str: String of version from __init__.py.

    Raises:
        ValueError: If no __version__ is find. Try set INIT_PATH...
    """

    if not INIT_PATH:
        INIT_PATH = paths.INIT_PATH

    with open(INIT_PATH, "r") as init_file:

        for line in init_file:

            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]

        else:
            raise ValueError(
                mylogging.return_str("__version__ variable not found in __init__.py. Try set INIT_PATH.")
            )


def run_tests(test_path=None, test_coverage=True):
    import pytest

    """Run tests. If any test fails, raise an error.

    Args:
        test_path ((str, pathlib.Path), optional): Usually autodetected (if ROOT_PATH / tests).
            Defaults to None.
        test_coverage(bool, optional): Whether run test coverage plugin. If True, pytest-cov must be installed. Defaults to True

    Raises:
        Exception: If any test fail, it will raise exception (git hook do not continue...).
    """

    if not test_path:
        test_path = paths.ROOT_PATH / "tests"

    if not test_coverage:
        pytest_args = ["-x", test_path.as_posix()]
    else:
        pytest_args = [
            "-x",
            "--cov",
            paths.APP_PATH.as_posix(),
            "--cov-report",
            "xml:.coverage.xml",
            test_path.as_posix(),
        ]

    pytested = pytest.main(pytest_args)

    if test_coverage:
        Path(".coverage").unlink()

    if pytested == 1:
        raise RuntimeError(mylogging.return_str("Pytest failed"))


def sphinx_docs_regenerate(docs_path=None, build_locally=False, git_add=True, exclude_paths=[]):
    """This will generate all rst files necessary for sphinx documentation generation with sphinx-apidoc.
    It automatically delete removed and renamed files.

    Note:
        All the files except ['conf.py', 'index.rst', '_static', '_templates'] will be deleted!!!
        Because if some files would be deleted or renamed, rst would stay and html was generated.
        If you have some extra files or folders in docs source - add it to `exclude_paths` list.

    Function suppose sphinx build and source in separate folders...

    Args:
        docs_path ((str, Path), optional): Where source folder is. Usually infered automatically.
            Defaults to None.
        build_locally (bool, optional): If true, build build folder with html files locally.
            Defaults to False.
        git_add (bool, optional): Whether to add generated files to stage. False mostly for
            testing reasons. Defaults to True.
        exclude_paths (list, optional): List of files and folder names that will not be deleted.
            ['conf.py', 'index.rst', '_static', '_templates'] are excluded by default. Defaults to [].

    Note:
        Function suppose structure of docs like::

            -- docs
            -- -- source
            -- -- -- conf.py
            -- -- make.bat

        If you are issuing error, try set project root path with `set_root`
    """

    if not importlib.util.find_spec("sphinx"):
        raise ImportError(
            mylogging.return_str(
                "Sphinx library is necessary for docs generation. Install via `pip install sphinx`"
            )
        )

    if not docs_path:
        if paths.ROOT_PATH:
            docs_path = paths.ROOT_PATH / "docs"
        else:
            raise NotADirectoryError(
                mylogging.return_str(
                    "`docs_path` not found. Setup it with parameter `docs_path` or use `paths.set_paths()` function."
                )
            )

    if not all([paths.APP_PATH, paths.ROOT_PATH]):
        mylogging.return_str("Paths are not known. First run `paths.set_paths()`.")

    docs_source_path = docs_path / "source"

    for p in Path(docs_source_path).iterdir():
        if p.name not in [
            "conf.py",
            "index.rst",
            "_static",
            "_templates",
            *exclude_paths,
        ]:
            try:
                p.unlink()
            except Exception:
                pass

    if build_locally:
        subprocess.run(["make", "html"], shell=True, cwd=docs_path, check=True)

    apidoc_command = f"sphinx-apidoc -f -e -o source {paths.APP_PATH.as_posix()}"
    subprocess.run(
        apidoc_command,
        shell=True,
        cwd=docs_path,
        check=True,
    )

    if git_add:
        subprocess.run(["git", "add", "docs"], shell=True, cwd=paths.ROOT_PATH, check=True)


def generate_readme_from_init(git_add=True):
    """Because i had very similar things in main __init__.py and in readme. It was to maintain news
    in code. For better simplicity i prefer write docs once and then generate. One code, two use cases.

    Why __init__? - Because in IDE on mouseover developers can see help.
    Why README.md? - Good for github.com

    If issuing problems, try paths.set_root() to library path.

    Args:
        git_add (bool, optional): Whether to add generated files to stage. False mostly
            for testing reasons. Defaults to True.
    """

    with open(paths.INIT_PATH) as fd:
        file_contents = fd.read()
    module = ast.parse(file_contents)
    docstrings = ast.get_docstring(module)

    if docstrings is None:
        docstrings = ""

    with open(paths.ROOT_PATH / "README.md", "w") as file:
        file.write(docstrings)

    if git_add:
        subprocess.run(["git", "add", "README.md"], shell=True, cwd=paths.ROOT_PATH, check=True)
