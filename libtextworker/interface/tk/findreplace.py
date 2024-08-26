"""
@package libtextworker.interface.tk.findreplace
@brief Find & Replace dialog(s)
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import tkinter
from tkinter.ttk import Button, Checkbutton, Frame, Label, Entry

from . import TK_USEGRID, actionrow, TK_USEPACK
from ... import _

class FindReplace(Frame):
    """
    A find-replace frame for Tkinter text editors.
    """

    Target: tkinter.Text
    LastIndex: str = "1.0"

    def __init__(this, master: tkinter.Misc, editor: tkinter.Text, placestyle = TK_USEGRID,
                 addReplace: bool = False, foundBackground: str = "yellow", *args, **kwds):
        """
        Constructor.

        @param master: The frame's parent
        @param editor: Target editor
        @param placestyle: How we need to place things (grid, pack)
        @param addReplace: Enable text replace function
        @param foundBackground: Match text's background color
        """
        Frame.__init__(this, master, *args, **kwds)
        this.Target = editor

        # UI Building
        if TK_USEGRID in placestyle:
            target = actionrow.ActionRow.PlaceObj
            leftside = {"column": -1}
            rightside = {"row": -1}
            currcolumn = 0 # Currently used column

            def placewidget(which):
                nonlocal currcolumn
                currcolumn += 1
                which.grid(row=0, column = currcolumn)
        else:
            if not TK_USEPACK in placestyle:
                from warnings import warn
                warn("TK_USEPLACE is not supported in FindReplace frame. Will use Pack method instead.")

            target = actionrow.ActionRow.PlaceObjPack
            leftside = {"side": "left"}
            rightside = {"side": "right"}

            def placewidget(which):
                which.pack(fill="x")

        ## Find entry
        row1 = actionrow.ActionRow(this)
        target(row1, Label, text=_("Find for:"), **leftside)
        this.find_var = tkinter.StringVar()
        # this.find_var.trace_add('write', lambda _, __, ___: this.Search())
        target(row1, Entry, justify="left", textvariable=this.find_var).bind("<KeyRelease>", lambda evt: this.Search())
        placewidget(row1)

        ## Replace buttons
        if addReplace:
            row2 = actionrow.ActionRow(this)
            this.replaceentry = target(row2, Entry, justify="left")
            target(row2, Label, text=_("Replace with:"))
            placewidget(row2)

            do2_row = actionrow.ActionRow(this)
            target(do2_row, Button, text=_("Replace"), **rightside).configure(command=lambda: this.Replace(1))
            target(do2_row, Button, text=_("Replace all"), **rightside).configure(command=lambda: this.Replace(2))
            placewidget(do2_row)

        ## Use regex
        regex_row = actionrow.ActionRow(this)
        target(regex_row, Label, side="right", text=_("Use regular expression"))
        this.regex_chk = tkinter.BooleanVar()
        target(regex_row, Checkbutton, variable=this.regex_chk)
        placewidget(regex_row)
        
        ## Case sensitive
        case_row = actionrow.ActionRow(this)
        target(case_row, Label, side="right", text=_("Case sensitive"))
        this.case_chk = tkinter.BooleanVar()
        target(case_row, Checkbutton, variable=this.case_chk)
        placewidget(case_row)

        # Set find matches color tag
        this.Target.tag_config("found", background=foundBackground)
    
    """
    Search for strings specified in the dialog.
    """
    def Search(this):
        text = this.find_var.get()
        pos = "1.0"
        this.Target.tag_remove("found", pos, "end")

        if text:

            while True:
                pos = this.Target.search(
                    text, # pattern
                    this.LastIndex, # index
                    'end', # stop index
                    nocase=not this.case_chk.get(),
                    regexp=this.regex_chk.get()
                )
                if not pos: break
                this.LastIndex = f"{pos}+{len(text)}c"
                this.Target.tag_add("found", this.LastIndex)
                pos = this.LastIndex
    
    """
    Replace using strings specified in the dialog.
    """
    def Replace(this, evt):
        index2 = this.LastIndex if evt == 1 else 'end'
        this.Target.replace(
            1.0, # from index
            index2, # to index
            this.Target.get(1.0, index2)
                       .replace(this.find_var.get(), this.replaceentry.get())
        )