"""
@package libtextworker.interface.tk.findreplace
@brief Find & Replace dialog(s)
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

from enum import auto
from tkinter.ttk import Frame, Label, Entry

from . import actionrow
from ... import _
from ...general import libTewException

FR_FIND = auto()
FR_REPLACE = auto()

class FindReplace(Frame):

    def __init__(this, master, style: int = -1, *args, **kwds):
        Frame.__init__(this, master, *args, **kwds)

        if FR_FIND in style:
            row1 = actionrow.ActionRow(this)
            row1.PlaceObjPack(Label, text=_("Find for:"), side="left")
            this.findentry = row1.PlaceObjPack(Entry, justify="left")

        if FR_REPLACE in style:
            row2 = actionrow.ActionRow(this)
            row2.PlaceObjPack(Label, text=_("Replace with:"), side="left")
            this.replaceentry = row2.PlaceObjPack(Entry, justify="left")

        if style == -1:
            raise libTewException("No style specified for FindReplace class.")
    