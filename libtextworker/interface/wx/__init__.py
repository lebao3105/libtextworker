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
from ..manager import ColorManager, hextorgb

if Importable["wx"] == True:
    import wx

    pass
else:
    raise Exception("wxPython is needed to use libtextworker.interface.wx")


class ColorManager(ColorManager):
    recursive_configure: bool = True

    def GetFont(self):
        size, style, weight, family = super().GetFont()

        _dict = {"system": "normal"}
        weight = _dict.get(weight, weight)
        style = _dict.get(style, style)

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
