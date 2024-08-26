#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import gettext
from .general import Importable, \
                     GetCurrentDir, CraftItems, test_import, \
                     TOPLV_DIR, EDITOR_DIR, THEMES_DIR

__all__ = ( "__version__", "EDITOR_DIR", "Importable", "THEMES_DIR", "TOPLV_DIR" )

# Setup translations

gettext.bindtextdomain("libtextworker", CraftItems(GetCurrentDir(__file__), "../po"))
gettext.textdomain("libtextworker")
_ = gettext.gettext

# libtextworker version
__version__ = "0.1.4b1"

## Dependency checks

if not test_import("watchdog"):
    from warnings import warn
    warn("watchdog module cannot be imported - file system watching wont work.")

test_import("configparser")
test_import("commentedconfigparser")
