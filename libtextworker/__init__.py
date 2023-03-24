"""
@package libtextworker
Library of the textworker project.

libtextworker contains customizable widgets and powerful settings system in order to make GUI apps greater!

How to use this library:
* make sure to have at least Python 3.8+, then choose a GUI framework (only wxPython for now, should not use on Python 3.11+)
* install requirements first (configparser, darkdetect, pillow)
* visit our online document (https://lebao3105.gitbook.io/libtextworker)
* include this project as a git submodule (if needed), also make this project a dependency of your project!

Public variables:
* Importable (dict) : GUI frameworks check
* \__version__ (str) : Library version
* THEMES_DIR (str, should not be edited) : Themes directory
* EDITOR_DIR (str, should not be edited) : Editor configurations directory
"""

import gettext
import os.path
import warnings

from .general import WalkCreation

# Setup translations
LOCALEDIR = "@LOCALEDIR@"
MESONTOUCHED = "@TOUCHED@"
APPDOMAIN = "libtextworker"

if not os.path.exists(LOCALEDIR) or MESONTOUCHED != "True":
    LOCALEDIR = "./po/"

gettext.bindtextdomain(APPDOMAIN, LOCALEDIR)
gettext.textdomain(APPDOMAIN)
gettext.install(APPDOMAIN, LOCALEDIR)

# Module import tests
Importable = {}

try:
    import wx
except ImportError:
    warnings.warn("wxPython not found. Skipping all relative imports...")
    Importable["interface.wx"] = False
else:
    Importable["interface.wx"] = True
finally:
    del wx

# Something else;-;
__version__ = "0.1.0"
THEMES_DIR = os.path.expanduser("~/.config/textworker/themes/")
EDITOR_DIR = os.path.expanduser("~/.config/textworker/editorconfigs/")

WalkCreation(THEMES_DIR)
WalkCreation(EDITOR_DIR)