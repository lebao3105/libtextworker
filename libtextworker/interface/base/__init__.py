# 	A cross-platform library for Python apps.
# 	Copyright (C) 2023 Le Bao Nguyen and contributors.
# 	This is a part of the libtextworker project.
# 	Licensed under the GNU General Public License version 3.0 or later.

"""
@package libtextworker.interface.base
@brief The base of all GUIs in libtextworker
"""
from enum import Flag, auto
from typing import Callable, Literal


class DC_FLAGS(Flag):
    """
    Flags for DirCtrl.
    """

    DC_ONEROOT = auto()  # Only one root to be allowed
    DC_EDIT = auto()  # Editable labels
    DC_HIDEROOT = auto()  # Hide root nodes
    DC_MULTIPLE = auto()  # Multiple selections
    DC_DIRONLY = auto()  # Show only directories
    DC_RIGHTCL = auto()  # Right click menu
    DC_DYNAMIC = auto()  # Watch for changes then refresh the widget itself
    DC_USEICON = auto()  # Use icons


class WidgetBase:
    """
    The base class for libtextworker GUI widgets.

    Use these variables before starting your work:
    * Parent_ArgName: parent widget keyword in __init__'s kwds
    * Styles: Widget styles, if able to use
    * _Frame: Not all widgets require this. GUI toolkit's Frame widget.
        If used, the actual widget will be placed into a frame.
    __init__ function will return the (modified) args + kwds.
    """

    Parent_ArgName: Literal["master", "parent", "Parent", "Master"] | str
    Styles: auto
    Frame: Callable | None = None
    _Frame: Callable | None = None

    def __init__(this, *args, **kwds):
        """
        Usually this is called in WidgetBase-derived classes in order to modify
            their args and kwds. The widget also will be placed into a frame if
            _Frame is specified.
        If not specified, do nothing.
        """

        try:
            # Get specific widget styles
            if "w_styles" in kwds:
                this.Styles = kwds["w_styles"]
                kwds.pop("w_styles")

            # Try to place the actual widget into a frame
            if this._Frame:
                # Get the target parent widget
                if not this.Parent_ArgName in kwds:
                    temp = list(args)
                    target_parent = temp[0]
                    temp.pop()
                    args = tuple(temp)
                else:
                    target_parent = kwds[this.Parent_ArgName]
                    kwds.pop(this.Parent_ArgName)

                this.Frame = this._Frame(**{this.Parent_ArgName: target_parent})

            return args, kwds

        except:
            return None
