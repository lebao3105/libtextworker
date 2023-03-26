"""
@package libtextworker.interface.wx
Contains classes for wxPython.
wxPython must be installed first:

    $ pip install attrdict3
    $ pip install wxPython
    
Else libtextworker will refuse to use this package.
"""

from libtextworker import Importable
from . import constants
from ..manager import ColorManager, default_configs

if Importable["interface.wx"] == True:
    import wx
    pass
else:
    raise Exception(
        "interface.wx is called but its dependency wxPython is not installed"
    )

class ColorManager(ColorManager):

    def _get_font(self):
        size, style, weight, family = super()._get_font()
        return wx.Font(constants.FONTSZ[size], wx.FONTFAMILY_DEFAULT, constants.FONTST[style], constants.FONTWT[weight], 0, family)

clrmgr = ColorManager(default_configs)