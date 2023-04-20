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
from ..manager import ColorManager, default_configs

if Importable["wx"] == True:
    import wx

    pass
else:
    raise Exception("wxPython is needed to use libtextworker.interface.wx")


class ColorManager(ColorManager):
    recursive_configure: bool = True

    def _get_color(self):
        back, fore = super()._get_color()
        back = "#" + "%02x%02x%02x" % back
        fore = "#" + "%02x%02x%02x" % fore
        return back, fore

    def _get_font(self):
        size, style, weight, family = super()._get_font()
        return wx.Font(
            size,
            wx.FONTFAMILY_DEFAULT,
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


clrmgr = ColorManager(default_configs)
