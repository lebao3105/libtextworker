#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import gettext
from warnings import warn

from .general import GetCurrentDir, CraftItems, Importable, TOPLV_DIR, test_import, EDITOR_DIR, THEMES_DIR

__all__ = ( "__version__", "EDITOR_DIR", "Importable", "LOG_PATH", "THEMES_DIR", "TOPLV_DIR" )

# Setup translations

gettext.bindtextdomain("libtextworker", CraftItems(GetCurrentDir(__file__), "../po"))
gettext.textdomain("libtextworker")
_ = gettext.gettext

# Else things

__version__ = "0.1.4b1" # Project version

## Dependencies checking

if not test_import("watchdog"):
    warn("watchdog module cannot be imported - file system watching wont work.")

test_import("configparser")
test_import("commentedconfigparser")
