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

if Importable["interface.wx"] == True:
    import wx

    pass
else:
    raise Exception(
        "interface.wx is called but its dependency wxPython is not installed"
    )


class ColorManager(ColorManager):
    recursive_configure: bool = True

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

        self.autocolor_run(widget)


clrmgr = ColorManager(default_configs)

class _entry_point(object): ...