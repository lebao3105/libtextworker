"""
@package libtextworker.interface.tk.findreplace
@brief Find & Replace dialog(s)
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import tkinter
from tkinter.ttk import Button, Frame, Label, Entry

from . import TK_USEGRID, actionrow, TK_USEPACK
from ... import _
from ...general import libTewException

class FindReplace(Frame):
    """
    A find-replace dialog for Tkinter text edits.
    """

    Target: tkinter.Text
    LastIndex: str = "1.0"

    def __init__(this, master, editor: tkinter.Text, placestyle = TK_USEGRID,
                 addReplace: bool = False, foundBackground: str = "yellow", *args, **kwds):
        Frame.__init__(this, master, *args, **kwds)
        this.Target = editor

        # UI Building
        # TODO: More find options, e.g case sensitive and regex
        if TK_USEGRID in placestyle:
            target = actionrow.ActionRow.PlaceObj
            leftside = {"column": -1}
        else:
            target = actionrow.ActionRow.PlaceObjPack
            leftside = {"side": "left"}

        row1 = actionrow.ActionRow(this)
        target(row1, Label, text=_("Find for:"), **leftside)
        this.findentry = target(row1, Entry, justify="left")
        row1.pack(expand=True, fill="x")

        do_row = actionrow.ActionRow(this)
        findbtn = target(do_row, Button, text=_("Find"))
        findbtn.configure(command=this.Search)
        do_row.pack(expand=True, fill="x")

        if addReplace:
            row2 = actionrow.ActionRow(this)
            this.replaceentry = row2.PlaceObjPack(Entry, justify="left")
            target(row2, Label, text=_("Replace with:"), **leftside)
            row2.pack(expand=True, fill="x")


            do2_row = actionrow.ActionRow(this)
            replacebtn = target(do2_row, Button, text=_("Replace"))
            replacebtn.configure(command=lambda: this.Replace(1))
            replaceall_btn = target(do2_row, Button, text=_("Replace all"))
            replaceall_btn.configure(command=lambda: this.Replace(2))
            do2_row.pack(expand=True, fill="x")

        result_row = actionrow.ActionRow(this)
        target(result_row, Label, **leftside)
        closebtn = target(result_row, Button, text=_("Close"))
        closebtn.configure(command=this.destroy)
        result_row.pack(expand=True, fill="x")

        # Configure found color tag
        this.Target.tag_config("found", background=foundBackground)
    
    def Search(this):
        text = this.findentry.get()
        this.Target.tag_remove("found", 1.0, "end")
        pos = "1.0"

        if text:
            while True:
                pos = this.Target.search(text, this.LastIndex, 'end', nocase=True, regexp=True)
                lastidx = f"{pos}+{len(text)}c"
                this.Target.tag_add("found", pos, lastidx)
                pos = lastidx
    
    def Replace(this, evt):
        this.Target.replace(1.0, this.LastIndex if evt == 1 else "END",
                            this.Target.get(1.0, "END").replace(this.findentry.get()))