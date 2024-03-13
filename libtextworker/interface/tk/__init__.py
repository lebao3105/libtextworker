"""
@package libtextworker.interface.tk
Contains class(es) and needed attributes for Tkinter.
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import typing
from enum import Flag, auto

from ...general import libTewException, test_import
from ..manager import ColorManager

if test_import("tkinter"):
    from tkinter import font, Misc, Menu
else:
    raise libTewException("Tkinter is not correctly installed!")

class TK_PLACEOPTS(Flag):
    TK_USEGRID = auto()
    TK_USEPLACE = auto()
    TK_USEPACK = auto()

TK_USEGRID = TK_PLACEOPTS.TK_USEGRID
TK_USEPLACE = TK_PLACEOPTS.TK_USEPLACE
TK_USEPACK = TK_PLACEOPTS.TK_USEPACK

class ColorManager(ColorManager):
    recursive_configure: bool = True
    is_shown: bool = False  # Messages

    def GetFont(self):
        size, style, weight, family = super().GetFont()
        font_families = font.families()

        if family == "default" or family not in font_families: family = "Consolas"

        if style != "italic": style = "roman"

        if weight not in ["system", "normal", "bold"] or weight == "system": # Looks stupid
            from warnings import warn
            warn("Tkinter font weight must be 'normal', 'system' (an alias to 'normal') or 'bold'")
            weight = "normal"

        return font.Font(None, family=family, weight=weight, slant=style, size=size)

    def setfontcfunc(self, objname: str, func: typing.Callable, params: dict):
        raise NotImplementedError

    def setcolorfunc(self, objname: str, func: typing.Callable, params: dict):
        raise NotImplementedError

    def configure(self, widget: Misc, color: str | None = None, childs_too: bool = recursive_configure):
        back, fore = self.GetColor(color)
        font_to_use = self.GetFont()

        if isinstance(widget, Menu):
            font_to_use.configure(size=10)
            if widget.index("end"):
                for i in range(0, int(widget.index("end"))):
                    widget.entryconfigure(i, background=back)

        try:
            widget.configure(font=font_to_use)
        except:
            pass

        # Why this catch?
        # Some Tkinter objects do not use fg and bg as their configure() keywords,
        # but use foreground and background instead.
        try:
            widget.configure(fg=fore, bg=back)
        except:
            pass

        try:
            widget.configure(background=back, foreground=fore)
        except:
            pass

        if childs_too:
            for child in widget.winfo_children():
                self.configure(child, color, True)
