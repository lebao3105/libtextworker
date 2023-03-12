import gettext
import os.path
import warnings

LOCALEDIR = "@LOCALEDIR@"
MESONTOUCHED = "@TOUCHED@"
APPDOMAIN = "libtextworker"

if not os.path.exists(LOCALEDIR) or MESONTOUCHED != "True":
    LOCALEDIR = "./po/"

gettext.bindtextdomain(APPDOMAIN, LOCALEDIR)
gettext.textdomain(APPDOMAIN)
gettext.install(APPDOMAIN, LOCALEDIR)

# Module import tests
Importable = {}

try:
    import wx
except ImportError:
    warnings.warn("wxPython not found. Skipping all relative imports...")
    Importable["interface.wx"] = False
else:
    Importable["interface.wx"] = True
finally:
    del wx