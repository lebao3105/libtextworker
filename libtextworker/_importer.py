# This script is used to test the import of
# GUI libraries, and the support of libtextworker for they.
import warnings
from importlib import import_module
from importlib.metadata import entry_points, EntryPoints

wx_load = entry_points(group='libtextworker.wx')
tk_load = entry_points(group='libtextworker.tkinter')

Importable = {}

def test_import(pkgname:str, ep: EntryPoints) -> bool:
    try:
        import_module(pkgname)
    except ImportError:
        Importable[pkgname] = False
        warnings.warn("%s not found" % pkgname)
    else:
        try:
            ep[0].load()
        except IndexError:
            warnings.warn(
                """
                {} found, but not you have not installed the support from libtextworker yet.\n
                Get it with the package libtextworker[{}]
                """.format(pkgname, pkgname)
            )

test_import('wx', wx_load)
test_import('tkinter', tk_load)