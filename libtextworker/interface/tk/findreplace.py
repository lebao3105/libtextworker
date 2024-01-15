from enum import auto
from tkinter import Toplevel
from tkinter.ttk import Frame, Label, Entry

from ...general import libTewException
from . import actionrow

FR_FIND = auto()
FR_REPLACE = auto()

class FindReplace(Frame):

    def __init__(this, master, style: int = -1, *args, **kwds):
        Frame.__init__(this, master, *args, **kwds)
        # Build the UI

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

class FindReplaceDialog(Toplevel):

    def __init__(this, *args, **kwds):
        Toplevel.__init__(this, *args, **kwds)