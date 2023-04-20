"""
@package libtextworker
Library of the textworker project.

libtextworker contains customizable widgets and powerful settings system in order to make GUI apps greater!

How to use this library:
* Make sure to have at least Python 3.8+, then choose a GUI framework (only wxPython for now, should not use on Python 3.11+)
* Install requirements first (configparser, darkdetect, pillow)
* Visit our online website (https://lebao3105.github.io/libtextworker)
* Include this project as a git submodule (if needed), also make this project a dependency of your project!

Public variables:
* Importable (dict) : GUI frameworks check
* \__version__ (str) : Library version
* THEMES_DIR (str, should not be edited) : Themes directory
* EDITOR_DIR (str, should not be edited) : Editor configurations directory
"""

import gettext
import os.path

from . import _importer
from .general import WalkCreation, GetCurrentDir, CraftItems

# Setup translations
LOCALEDIR = CraftItems(GetCurrentDir(__file__), "po")
APPDOMAIN = "libtextworker"  ## Project app domain

if not os.path.exists(LOCALEDIR):
    LOCALEDIR = CraftItems(GetCurrentDir(__file__), "../po")

gettext.bindtextdomain(APPDOMAIN, LOCALEDIR)
gettext.textdomain(APPDOMAIN)
gettext.install(APPDOMAIN, LOCALEDIR)

# Module import tests
Importable = _importer.Importable

# Something else;-;
__version__ = "0.1.2"
THEMES_DIR = os.path.expanduser(
    "~/.config/textworker/themes/"
)  ## Directory of *custom* themes
EDITOR_DIR = os.path.expanduser(
    "~/.config/textworker/editorconfigs/"
)  ## Directory of *editor configurations

WalkCreation(THEMES_DIR)
WalkCreation(EDITOR_DIR)
