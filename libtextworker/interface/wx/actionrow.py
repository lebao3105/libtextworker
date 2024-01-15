"""
@package libtextworker.interface.wx.actionrow
"""
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
    def Parent(self):
        """
        The actual parent of this widget.
        """
        return self._Parent

    @Parent.setter
    def Parent(self, obj: wx.Control):
        self._Parent = obj

    def SetParent(self, obj: wx.Control):
        """
        Make wxActionRow know its parent, where widgets will set their parent to.
        """
        self.Parent = obj

    def PlaceObj(self, obj: wx.Control, stretch: int = 1, *args, **kwds) -> wx.Control:
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

        kwds["parent"] = self.Parent
        target = obj(*args, **kwds)

        self.Add(target, stretch, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        return target