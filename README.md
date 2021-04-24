# mypythontools

[![Python versions](https://img.shields.io/pypi/pyversions/mypythontools.svg)](https://pypi.python.org/pypi/mypythontools/) [![PyPI version](https://badge.fury.io/py/mypythontools.svg)](https://badge.fury.io/py/mypythontools) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Malachov/mypythontools.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Malachov/mypythontools/context:python) [![Documentation Status](https://readthedocs.org/projects/mypythontools/badge/?version=latest)](https://mypythontools.readthedocs.io/en/latest/?badge=latest) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![codecov](https://codecov.io/gh/Malachov/mypythontools/branch/master/graph/badge.svg)](https://codecov.io/gh/Malachov/mypythontools)

Some tools/functions/snippets used across projects.

## Links

Official documentation - [readthedocs](https://mypythontools.readthedocs.io/)

Official repo - [github](https://github.com/Malachov/mypythontools)

It's called mypythontools, but it's also made for you...

Usually used from IDE. Used paths are infered and things like sphinx rst docs generation, building
application with pyinstaller or deploying to Pypi is matter of calling one function,
or clicking one button (e.g. Vs code task).

Many projects - one codebase.

If you are not sure whether structure of your app will work with this code, check `project-starter` on github in content folder.

Paths are infered, but if you have atypical structure or have more projects in cwd, use `mypythontools.misc.set_paths()`.

## Modules

- build
- deploy
- misc
- pyvueeel (for applications build with eel and vue)
- utils (various functions callable from one `push_pipeline` function)

Check modules help with examples.

## Installation

Python >=3.6 (Python 2 is not supported).

Install just with

```console
pip install mypythontools
```

## Content

There are some other things that are not installed via pip in mypythontools library.

### project-starter

Project scaffolding fast and easy.

Download project-starter from (github)[https://github.com/Malachov/mypythontools/tree/master/content/project-starter] (You may need to download all mypythontools repository in zip)

And start developing.

In your IDE do bulk renaming across files and replace `SET_YOUR_APP_NAME` with name of your app / library.

This starter is for vue-eel applications (desktop as well as web) but also for python libraries that will be stored on Pypi.

If it's python library, delete `gui` folder.

If it's app with gui, delete `setup.py` and remove **Installation** and **Modules** from README.
Also from assets delete `mdi.css` if not using icons and `formulate.css` if not using **vue formulate**.
In `package.json` uncomment library you will be using. Then check `pyvueell` module

Delete is faster than write, so there is many examples like for example plot, various formating, settings panel, function call from both sides or automatic alerting from python.

This is how the example looks like

<div align="center"><img src="docs/source/_static/project-starter-gui.png" width="620" alt="project-starter-gui"/></div>

**Docs**
It includes docs structure for sphinx docs generations from docstrings. Edit first few lines in conf.py, index.rst, navi.html and if you want, add static files like logo to \_static.

Usually used with [readthedocs](https://readthedocs.org/) free hosting that trigger deploy automatically after pushing to master. Because of correct relative redirecting in index.rst and navi.html use for readthedocs /path/ before relative link to ohter module.

It's also necassary to generate other modules rst files for other pages but it's if using `push_script.py` as CI/CD (see below), it's generated automatically via `apidoc`.

It's recommended to use with `sphinx-alabaster-css` (see below).

**CI/CD**
It also include github actions yml file for pushing codecov coverage file (without token) and .travis.yml for Travis CI. You don't need those files and can you can delete it.

There is file `push_script.py` in folder `utils` which personally is better (faster) than travis and can do most of what you want from CI like run pipeline - running tests / generate docs / increment version / push to github / push to pypi.

Check utils module for more informations.

**IDE files**
It also include some default project specific settings for VS Code. You can also delete it.

If developing py - vue - eel app this is the recommended way, but if you want to build just what is necassaty from scratch, you can use this tutorial [readthedocs](https://mypythontools.readthedocs.io/mypythontools.pyvueeel.html#mypythontools.pyvueeel.help_starter_pack_vue_app).

### requirements

Install many libraries at once (no need for Anaconda). Download `requirements.txt` file from (github)[https://github.com/Malachov/mypythontools/tree/master/content/requirements] and in that folder use

```
pip install -r requirements.txt
```

It's good for python libraries that other users with different versions of libraries will use. If not standalone application where freezing into virtual env is good idea - here is possible to use this requirements with using --upgrade from time to time to be sure that your library will be working for up to date version of dependencies.

### sphinx-alabaster-css

It's good idea to generate documentation from code. If you are useing sphinx and alabaster theme, you can use this css file for formating.

Tested on readthedocs hosting (recommended).

CSS are served from github and it's possible to change on one place and edit how all projects docs look like at once.

Just add this to sphinx conf.py

```
html_css_files = [
    "https://malachov.github.io/readthedocs-sphinx-alabaster-css/custom.css",
]
```

Also of course if you want you can download it and use locally from project if you need.

Result should look like this

<div align="center"><img src="docs/source/_static/sphinx-alabaster-css.png" width="620" alt="sphinx-alabaster-css"/></div>

### Tasks

There are VS Code tasks examples in utils and build module, but here is small tutorial how to use it.
Run command `Tasks: Open User Tasks`, add tasks from github/content/tasks or if have no task yet, you can copy / paste all.

Install extension **Task Explorer**

On root copy folder `utils` from content/tasks

You are ready to go. You should see something like this

<div align="center"><img src="docs/source/_static/tasks.png" width="620" alt="tasks"/></div>

You can do CI / CD pipeline or Build app with one click now.
