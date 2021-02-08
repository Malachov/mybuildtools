"""
Common functions for Python / Vue / Eel project.

Run `mypythontools.pyvueel.help_starter_pack_vue_app()` for tutorial how to create such an app.

"""

import os
import sys
from pathlib import Path
import warnings
import pandas as pd
import numpy as np

import mylogging

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', module='eel', category=ResourceWarning)

    import eel


def run_gui(multiprocessing=False, log_file_path=None):
    """Function that init and run `eel` project.
    It will autosetup chrome mode (if installed chrome or chromium, open separate window with
    no url bar, no bookmarks etc...) if not chrome installed, it open microsoft Edge (by default on windows).

    # TODO document more
    # In devel mode, app is connected on live vue server.

    Args:
        multiprocessing (bool, optional): If using multiprocessing in some library, set up to True. Defaults to False.
        log_file_path ((str, Path, None)), optional): If not exist, it will create, if exist, it will append,
        if None, log to relative log.log and only if in production mode.
    """

    try:
        devel = False if os.environ.get('MY_PYTHON_VUE_ENVIRONMENT') == 'production' else True

        if log_file_path:
            log_file = log_file_path
        else:
            log_file = 'log.log' if not devel else None

        mylogging.config.TO_FILE = log_file

        if getattr(sys, 'frozen', False):
            gui_path = Path(sys._MEIPASS) / 'gui'
        else:
            gui_path = Path(__file__).resolve().parent / 'gui'

        if devel:
            directory = gui_path / 'src'
            app = None
            page = {'port': 8080}
            port = 8686

            def close_callback(page, sockets):
                pass

        else:
            directory = gui_path / 'web_builded'
            close_callback = None
            app = 'chrome'
            page = 'index.html'
            port = 0

        eel.init(directory.as_posix(), ['.vue', '.js', '.html'])

        # try:
        # if devel:

        # If server is not running, it's started automatically
        # import psutil
        # import subprocess

        # import signal
        # already_run = 8080 in [i.laddr.port for i in psutil.net_connections()]

        # if not already_run:

        #     subprocess.Popen(f"cd '{pystore.gui_path.as_posix()}' && npm run serve", stdout=subprocess.PIPE,
        #                      shell=True)
        #     print("\nVue starting, reload page after loaded! \n")
        #     import webbrowser
        #     webbrowser.open('http://localhost:8080/', new=2)

        if multiprocessing:
            multiprocessing.freeze_support()

        mylogging.info("Py side started")

        eel.start(page, mode=app, cmdline_args=['--disable-features=TranslateUI'], close_callback=close_callback, host='localhost', port=port, disable_cache=True),

    except OSError:
        eel.start(page, mode='edge', host='localhost', close_callback=close_callback, port=port, disable_cache=True),


    except Exception:
        mylogging.traceback("Py side terminated...")


def help_starter_pack_vue_app():
    """
    Tutorial how to build app with python, Vue and eel.
    Print help on build Vue part with CLI (many options, rather not copying files from other project).
    Then will help with basic structre of components, then show copypasters to other places.

    Structure

    - myproject
        - gui
            - generated with Vue CLI
        - app.py

    ############
    ### app.py
    ###########

    from mypythontools import pyvueel

    # Expose python functions to Js with decorator
    @eel.expose
        def load_data(settings):
            # You can return dict - will be object in js
            # You can return list - will be an array in js

            return {'Hello': 1}

    # End of file
    if __name__ == '__main__':
        pyvueel.run_gui()

    #########
    ### gui
    ########

    Generate gui folder with Vue CLI

    ```console
    npm install -g @vue/cli
    vue create gui
    ```

    Goto folder and

    ```console
    vue add vuex
    vue add router
    ```

    #############
    ### main.js
    ############

    if (ProcessingInstruction.env.NODE_ENV !== 'production') {
      window.eel.set_host("ws://localhost:8686")
    }

    // You can expose function to be callable from python. Import and then
    // window.eel.expose(mutate, 'mutate')

    ##########
    ### .env
    #########

    create empty files .env.development and add `VUE_APP_EEL=http://localhost:8686/eel.js`

    create empty .env.production and add `VUE_APP_EEL=eel.js`

    #################
    ### index.html
    ###############

    In public folder

    ```
    <script type="text/javascript" src="<%= VUE_APP_EEL %>"></script>
    ```

    #################
    ### Tips, trips
    ################

    # VS Code plugins for developing
    - npm
    - vetur
    - Vue VSCode Snippets
    - vuetify-vscode
    """

    print(help_starter_pack_vue_app.__doc__)


def json_to_py(json):
    """Take json / json from JS side and eval it from strings.
    If string to string, if float to float, if object then to dict.

    When to use? - If sending object as parameter in function.

    Args:
        json (dict): Object from JS

    Returns:
        dict: Python dictionary with correct types.
    """

    evaluated = {}
    for i, j in json.items():
        try:
            evaluated[i] = eval(j)
        except Exception:
            evaluated[i] = j
    return evaluated


def to_vue_plotly(data, names=None):
    """Takes data (dataframe or numpy array) and transforms it to form, that vue-plotly understand.

    Args:
        data ((np.array, pd.DataFrame)): Plotted data.
        names (list, optional): If using array, you can define names. Defaults to None.

    Returns:
        dict: Data in form for plotting in frontend.
    """
    if isinstance(data, (np.ndarray, np.generic)):
        data = pd.DataFrame(data, columns=names)

    numeric_data = data.select_dtypes(include='number').round(decimals=3)
    numeric_data = numeric_data.where(np.isfinite(numeric_data), None)
    # numeric_data = add_none_to_gaps(numeric_data)

    return {'x_axis': numeric_data.index.to_list(), 'y_axis': numeric_data.values.T.tolist(), 'names': numeric_data.columns.values.tolist()}


def to_table(df):
    """Takes data (dataframe or numpy array) and transforms it to form, that vue-plotly understand.

    Args:
        df (pd.DataFrame): Data in table form

    Returns:
        dict: Data in form for create table.
    """
    data = df.copy()
    data = data.round(decimals=3)

    # Numpy nan cannot be send to json - replace with None
    data = data.where(~data.isin([np.nan, np.inf, -np.inf]), None)

    headers = [{'text': i, 'value': i, 'sortable': True} for i in data.columns]

    return {'table': data.to_dict('records'), 'headers': headers}