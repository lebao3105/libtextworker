"""
@package libtextworker.interface.wx.actionrow
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import wx

class ActionRow(wx.BoxSizer):
    """
    Inspired from libadwaita/Gtk's ActionRow class,
    wxActionRow is a vertical (layout) wxBoxSizer with
        text on the left, buttons/clicks on the right.
    What to know here before adding widgets:
    - All widgets use proportion=1 to justify their side.
    - For wxCheckBox/OptionBox/Switch, you will want to turn off its text.'
    - When placing this widget you must NOT use stretch.
    """

    @property
    def Parent(this):
        """
        The actual parent of this widget.
        """
        return this._Parent

    @Parent.setter
    def Parent(this, obj: wx.Control):
        this._Parent = obj

    def SetParent(this, obj: wx.Control):
        """
        Make wxActionRow know its parent, where widgets will set their parent to.
        """
        this.Parent = obj

    def PlaceObj(this, obj: wx.Control, stretch: int = 1, *args, **kwds) -> wx.Control:
        """
        Place a widget from the LEFT.
        For overriding existing widgets,
            use Remove(index) first.
        Your widget will take wxActionRow.Parent as its parent.

        @param obj (wx.Control): a wxPython widget, but DON'T create any
            instance yet - pass it as a class/function name.
        @param stretch (int): defaults to 1 - proportion value for the sizer item.
            Recommended to use 1 most times - 0 to prevent stretching.
        @param *args (tuple): parameters to pass to your widget
        @param **kwds (dict[str]): the same work as *args.
        @return wx.Control: initialized & added-to-sizer widget
        """

        kwds["parent"] = this.Parent
        target = obj(*args, **kwds)

        this.Add(target, stretch, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        return target