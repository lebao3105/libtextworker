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
GITHUB_URL = "https://github.com/lebao3105/libtextworker"
API_URL = "https://lebao3105.github.io/libtextworker"
