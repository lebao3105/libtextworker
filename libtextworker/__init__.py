import gettext
import os.path

from .general import WalkCreation, GetCurrentDir, CraftItems, Importable, TOPLV_DIR

__all__ = (
    "__version__",
    "EDITOR_DIR" "Importable",
    "LICENSES",
    "LOG_PATH",
    "THEMES_DIR",
    "TOPLV_DIR",
)

# Setup translations
LOCALEDIR = CraftItems(GetCurrentDir(__file__), "po")
APPDOMAIN = "libtextworker"  ## Project app domain

if not os.path.exists(LOCALEDIR):
    LOCALEDIR = CraftItems(GetCurrentDir(__file__), "../po")

gettext.bindtextdomain(APPDOMAIN, LOCALEDIR)
gettext.textdomain(APPDOMAIN)
gettext.install(APPDOMAIN, LOCALEDIR)

# Something else;-;
__version__ = "0.1.4"
THEMES_DIR: str = ""
EDITOR_DIR: str = ""
LICENSES = rf'{os.path.normpath(CraftItems(GetCurrentDir(__file__), "licenses"))}'
LOG_PATH = os.path.expanduser("~/.logs/libtew.log")

# WalkCreation(THEMES_DIR)
# WalkCreation(EDITOR_DIR)
WalkCreation(rf'{os.path.expanduser("~/.logs")}')
