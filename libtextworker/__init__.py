#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import gettext
import os.path

from .general import GetCurrentDir, CraftItems, Importable, TOPLV_DIR

__all__ = ( "__version__", "EDITOR_DIR", "Importable", "LOG_PATH", "THEMES_DIR", "TOPLV_DIR" )

# Setup translations
LOCALEDIR = CraftItems(GetCurrentDir(__file__), "po")

if not os.path.exists(LOCALEDIR):
    LOCALEDIR = CraftItems(GetCurrentDir(__file__), "../po")

gettext.bindtextdomain("libtextworker", LOCALEDIR)
gettext.textdomain("libtextworker")
_ = gettext.gettext

# Something else;-;
__version__ = "0.1.4b1"
TOPLV_DIR: str
