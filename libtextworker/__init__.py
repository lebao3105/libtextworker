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
__version__ = "0.1.4"
THEMES_DIR = rf'{os.path.expanduser("~/.config/textworker/themes/")}'
EDITOR_DIR = rf'{os.path.expanduser("~/.config/textworker/editorconfigs/")}'
LICENSES = rf'{os.path.abspath(CraftItems(GetCurrentDir(__file__), "licenses"))}'

WalkCreation(THEMES_DIR)
WalkCreation(EDITOR_DIR)
WalkCreation(rf'{os.path.expanduser("~/.logs")}')
