import sys

sys.path.append("../libtextworker")
from libtextworker.general import CraftItems, GetCurrentDir

THEMEPATH = CraftItems(GetCurrentDir(__file__), "custom_theme.ini")
GITHUB_URL = "https://github.com/lebao3105/libtextworker"
API_URL = "https://lebao3105.github.io/libtextworker"
