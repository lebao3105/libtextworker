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
    DC_ONEROOT = auto()
    DC_DIRONLY = auto()
    DC_RIGHTCL = auto()
    DC_DYNAMIC = auto()
    DC_SCROLLB = auto()
    DC_USEICON = auto()

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
        
        # Get specific widget styles
        if "w_styles" in kwds:
            this.Styles = kwds["w_styles"]
            kwds.pop("w_styles")

        # Make sure we don't have 2 parents in __init__:)
        if not this.Parent_ArgName in kwds:
            temp = list(args)
            target_parent = temp[0]
            temp.pop()
            args = tuple(temp)
        else:
            target_parent = kwds[this.Parent_ArgName]
            kwds.pop(this.Parent_ArgName)

        if this._Frame:
            this.Frame = this._Frame(**{this.Parent_ArgName: target_parent})

        return args, kwds