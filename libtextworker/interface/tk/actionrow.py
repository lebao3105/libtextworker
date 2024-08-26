"""
@package libtextworker.interface.tk.actionrow
ActionRow class for Tkinter.
ActionRow is a vertical (layout) tkinter.Frame that is used for a specific action.
Useful for creating Settings pages.
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import tkinter
import tkinter.ttk

class ActionRow(tkinter.Frame):
    """
    Inspired from libadwaita's ActionRow class,
    tkActionRow is a horizontal (layout) tkinter.Frame with
        text on one side, and everything else like buttons on the other side.
    All in one row.
    """

    _curr_col: int = 0

    def PlaceObj(this, obj: tkinter.Misc, column: int | str = -1,
                 sticky: str = "e", *args, **kwds) -> tkinter.Misc:
        """
        Place a widget using grid method.
        @param obj (tkinter.Misc): What widget to place (class/function reference, NOT an instance)
        @param column (int): Where to place (row is always 0). -1 will place the widget next to the last one.
        @param sticky (str): Sticky option
        @param args, kwds: Options for the widget to place

        Returns created widget.
        """

        if len(args) >= 1:
            temp = list(args)
            temp[0] = this
            args = tuple(temp)
            del temp
        else:
            kwds["master"] = this

        target = obj(*args, **kwds)
        target.grid(column=column if column > -1 else this._curr_col + 1, row=0, sticky=sticky)
        this._curr_col += 1
        return target
    
    def PlaceObjPack(this, obj: tkinter.Misc, side: str = "right",
                     expand: bool = True, fill: str = "x",
                     *args, **kwds) -> tkinter.Misc:
        """
        Places a widget using pack method.
        @param obj (tkinter.Misc): What widget to place (class/function reference, NOT an instance)
        @param side, expand, fill: Pack options
        @param args, kwds: Options for the widget to place

        Returns the created widget
        """
        
        if len(args) >= 1:
            temp = list(args)
            temp[0] = this
            args = tuple(temp)
            del temp
        else:
            kwds["master"] = this
        
        target = obj(*args, **kwds)
        target.pack(expand=expand, fill=fill, side=side)
        return target
