import os
from typing import Callable
from libtextworker.general import libTewException
from . import DC_FLAGS, WidgetBase

DC_ONEROOT = DC_FLAGS.DC_ONEROOT
DC_DIRONLY = DC_FLAGS.DC_DIRONLY
DC_RIGHTCL = DC_FLAGS.DC_RIGHTCL
DC_DYNAMIC = DC_FLAGS.DC_DYNAMIC
DC_SCROLLB = DC_FLAGS.DC_SCROLLB
DC_USEICON = DC_FLAGS.DC_USEICON

class DirCtrlBase(WidgetBase):
    """
    A directory tree.
    Styles:
    * DC_ONEROOT: Only one root can be used
    * DC_DIRONLY: Show only directories
    * DC_RIGHTCL: Right-click menu
    * DC_DYNAMIC: Use watchdog to watch directory changes, if any redraw the widget
    * DC_SCROLLB: Use scrollbars
    * DC_USEICON: Use icons

    Enabled by default:
    * DC_DYNAMIC
    * DC_SCROLLB

    Features can be different on different platforms - this depends on the developer.
    The actual tree, also scrollbars if enabled - must be placed in a frame (named Frame).
    Custom flags (styles above) should be checked & implemented manually.
    """
    
    Styles = DC_DYNAMIC | DC_SCROLLB
    
    def SetFolder(this, path: str, newroot: bool):
        """
        Make DirCtrl to show a directory tree.
        If the directory is already used, will find that one and redraw.
        @param path (str): Target folder
        @param newroot (bool): Multiple root? Depends on DC_ONEROOT flag not to be included.
        """
        
        path = os.path.normpath(path)
        if not os.path.isdir(path): raise NotADirectoryError(path)

        if DC_ONEROOT in this.Styles and newroot == True:
            raise libTewException(
                "DirCtrl.SetFolder: Attemping to create a new root node but"
                "DC_ONEROOT style is enabled, which blocks that behaviour."
                "Report this to the developer."
            )
        
    def GetFullPath(this, item: str | Callable | None = None, event: Callable | None = None) -> str:
        """
        Get the full path of an item if specified, else the path of the curernt selection.
        @param event (Callable | None): GUI toolkit's event. Optional.
        @param item (str | Callable | None). Item to use.
        @returns str
        """
