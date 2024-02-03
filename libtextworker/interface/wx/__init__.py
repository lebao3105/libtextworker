"""
@package libtextworker.interface.wx
Contains classes for wxPython.
wxPython must be installed first:

    $ pip install attrdict3
    $ pip install wxPython
    
Else libtextworker will refuse to use this package.
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

from libtextworker import Importable
from . import constants
from .. import manager

if Importable["wx"] == True:
    import wx
else:
    raise Exception("wxPython is needed to use libtextworker.interface.wx")


class ColorManager(manager.ColorManager):
    recursive_configure: bool = True

    def GetFont(self):
        size, style, weight, family = manager.ColorManager.GetFont()

        _dict = {"system": "normal"}
        weight = _dict.get(weight, weight)
        style = _dict.get(style, style)

        return wx.Font(size, wx.FONTFAMILY_MODERN, constants.FONTST[style],
                       constants.FONTWT[weight], 0, family)

    def configure(self, widget: wx.Control, childs_too: bool = recursive_configure):
        manager.ColorManager.configure(widget)

        # fore&back
        bg, fg = self.GetColor()
        bg = wx.Colour(*manager.hextorgb(bg))
        fg = wx.Colour(*manager.hextorgb(fg))

        # font
        font = self.GetFont()

        if childs_too and hasattr(widget, "GetChildren"):
            widget.SetBackgroundColour(bg)
            widget.SetForegroundColour(fg)
            for children in widget.GetChildren():
                self.configure(children, True)
        else:
            widget.SetOwnBackgroundColour(bg)
            widget.SetOwnForegroundColour(fg)

        widget.SetFont(font)

## @deprecated On version 0.1.3
clrmgr = None
