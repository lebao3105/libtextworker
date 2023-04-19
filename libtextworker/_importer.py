# This script is used to test the import of
# GUI libraries, and the support of libtextworker for they.
import warnings
from importlib import import_module

Importable = {}


def test_import(pkgname: str) -> bool:
    try:
        import_module(pkgname)
    except ImportError:
        Importable[pkgname] = False
        warnings.warn("%s not found" % pkgname)
        return False
    else:
        Importable[pkgname] = True
        return True


test_import("wx")
test_import("tkinter")
