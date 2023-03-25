"""
@package libtextworker.interface.wx
Contains classes for wxPython.
wxPython must be installed first:

    $ pip install attrdict3
    $ pip install wxPython
    
Else libtextworker will refuse to use this package.
"""

from libtextworker import Importable

if Importable["interface.wx"] == True:
    pass
else:
    raise Exception(
        "interface.wx is called but its dependency wxPython is not installed"
    )
