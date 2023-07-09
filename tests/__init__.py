import sys
sys.path.append("../libtextworker")
from libtextworker.general import CraftItems, GetCurrentDir
THEMEPATH = CraftItems(GetCurrentDir(__file__), "custom_theme.ini")