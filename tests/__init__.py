# 	A cross-platform library for Python apps.
# 	Copyright (C) 2023 Le Bao Nguyen and contributors.
# 	This is a part of the libtextworker project.
# 	Licensed under the GNU General Public License version 3.0 or later.
import sys

sys.path.append("../libtextworker")

import libtextworker
from libtextworker.general import CraftItems, GetCurrentDir, TOPLV_DIR

TOPLV_DIR = GetCurrentDir(__file__)
libtextworker.THEMES_DIR = libtextworker.EDITOR_DIR = TOPLV_DIR

THEMEPATH = CraftItems(TOPLV_DIR, "custom_theme.ini")
REPO_URL = "https://gitlab.com/textworker/libtextworker_py"
API_URL = "https://lebao3105.github.io/libtextworker"

HAS_ACOLOR: str = \
    "You have it! Try manually togging the OS color scheme to see how the system works.\n" \
    "Not all widgets are able to work with the auto coloring system right now."

HASNT_ACOLOR: str = \
    "The auto coloring system isn't available here because of either:\n" \
    "* You have not installed darkdetect package;\n" \
    "* darkdetect does not support your system;\n" \
    "* auto attribute under custom_theme.ini's color section is turned off or invalid (must be 'yes' without quotes)"


def hasAutoColor() -> bool:
    from libtextworker.interface.manager import AUTOCOLOR
    return AUTOCOLOR