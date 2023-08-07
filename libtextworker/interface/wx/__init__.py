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
from ..manager import ColorManager

if Importable["wx"] == True:
    import wx

    pass
else:
    raise Exception("wxPython is needed to use libtextworker.interface.wx")


class ColorManager(ColorManager):
    recursive_configure: bool = True

    def GetFont(self):
        size, style, weight, family = super().GetFont()

        if style == "system":
            style = "normal"
        if weight == "system":
            weight = "normal"

        return wx.Font(
            size,
            wx.FONTFAMILY_MODERN,
            constants.FONTST[style],
            constants.FONTWT[weight],
            0,
            family,
        )

    def configure(self, widget: wx.Control, childs_too: bool = recursive_configure):
        super().configure(widget)

        # fore&back

        def hextorgb(value: str):
            lv = len(value)
            return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

        bg, fg = self.GetColor()
        bg = wx.Colour(*hextorgb(bg))
        fg = wx.Colour(*hextorgb(fg))

        # font
        font = self.GetFont()

        ## will this work?
        if childs_too and hasattr(widget, "GetChildren"):
            widget.SetBackgroundColour(bg)
            widget.SetForegroundColour(fg)
            widget.SetFont(font)
        else:
            widget.SetOwnBackgroundColour(bg)
            widget.SetOwnForegroundColour(fg)
            widget.SetOwnFont(font)

## @deprecated On version 0.1.3
clrmgr = None
