"""
@package libtextworker.interface.wx
Contains classes for wxPython.
wxPython must be installed first:

    $ pip install attrdict3
    $ pip install wxPython
    
Else libtextworker will refuse to use this package.
"""
import typing
from libtextworker import Importable
from . import constants
from ..manager import ColorManager

if Importable["wx"] == True:
    import wx

    pass
else:
    raise Exception("wxPython is needed to use libtextworker.interface.wx")


class ColorManager(ColorManager):
    recursive_configure: bool = True

    def _get_font(self):
        size, style, weight, family = super()._get_font()
        
        if style == "system": style = "normal"
        if weight == "system": weight = "normal"

        return wx.Font(
            size,
            wx.FONTFAMILY_MODERN,
            constants.FONTST[style],
            constants.FONTWT[weight],
            0,
            family,
        )

    def configure(self, widget: typing.Any, childs_too: bool = False):
        super().configure(widget)

        if childs_too and hasattr(widget, "GetChildren"):
            for child in widget.GetChildren():
                self.configure(child, self.recursive_configure)
                self.autocolor_run(child)


## @deprecated On version 0.1.3
clrmgr = None
