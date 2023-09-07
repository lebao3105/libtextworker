#	A cross-platform library for Python apps.
#	Copyright (C) 2023 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

"""
@package libtextworker.interface.base.dirctrl
@brief The base of DirCtrl - directory tree widget
TODO: Items sorting support
"""
import os
from libtextworker.general import libTewException
from typing import Callable, Literal, Any
from . import DC_FLAGS, WidgetBase

DC_ONEROOT = DC_FLAGS.DC_ONEROOT
DC_EDIT = DC_FLAGS.DC_EDIT
DC_HIDEROOT = DC_FLAGS.DC_HIDEROOT
DC_MULTIPLE = DC_FLAGS.DC_MULTIPLE
DC_DIRONLY = DC_FLAGS.DC_DIRONLY
DC_RIGHTCL = DC_FLAGS.DC_RIGHTCL
DC_DYNAMIC = DC_FLAGS.DC_DYNAMIC
DC_USEICON = DC_FLAGS.DC_USEICON

class DirCtrlBase(WidgetBase):
    """
    A directory tree.
    Styles are defined in ..DC_FLAGS class and called in this module.

    Enabled by default:
    * DC_DYNAMIC (feature not implemented)
    * DC_EDIT (toolkit-specific)
    * DC_USEICON (toolkit-specific)

    Features can be different on different platforms - this depends on the developer.
    The actual tree, also scrollbars if enabled - must be placed in a frame (named Frame).
    Custom flags (styles above) should be checked & implemented manually.
    """
    
    currpath: str
    Styles = DC_DYNAMIC | DC_EDIT | DC_USEICON
    History: dict[Any, list[str]]
    HistoryIdx: int = 0
    
    def SetFolder(this, path: str, newroot: bool):
        """
        Make DirCtrl to show a directory tree.
        If the directory is already used, will find that one and redraw.
        @param path (str): Target folder
        @param newroot (bool): Multiple root? Depends on DC_ONEROOT flag not to be included.
        """
        
        path = os.path.normpath(path)
        if not os.path.isdir(path):
            raise NotADirectoryError(path)
        else:
            this.currpath = path

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
    
    def GoForward(this):
        print(this.History)
        if this.History and this.HistoryIdx < len(this.History):
            this.SetFolder(this.History[this.HistoryIdx + 1])
            this.HistoryIdx = this.HistoryIdx + 1
        else: return
        this.PostSetDir(this.History[this.HistoryIdx], "forward")

    def GoBack(this):
        print(this.History)
        if this.History and this.HistoryIdx > 0:
            this.SetFolder(this.History[this.HistoryIdx - 1])
            this.HistoryIdx = this.HistoryIdx - 1
        else: return
        this.PostSetDir(this.History[this.HistoryIdx], "back")
    
    def PostSetDir(this, path, mode: Literal["forward", "back", "go"]) -> bool:
        if not this.History or this.HistoryIdx: return False
        if mode == "forward":
            if this.HistoryIdx == len(this.History): return False # Can't go forward
            else: this.HistoryIdx = this.HistoryIdx + 1
        if mode == "back":
            if this.HistoryIdx == 0: return False # Can't go back
            else: this.HistoryIdx = this.HistoryIdx - 1
        if mode == "go":
            if this.HistoryIdx not in [0, len(this.History)]:
                for i in range(this.HistoryIdx, len(this.History)):
                    this.History.pop(i)
            this.History.append(path)
            this.HistoryIdx = len(this.History)

    # By default os.path.getsize/os.stat.st_size output will return a value in bytes
    # So this is how we convert it to other units
    # *from SO: a/1094933*
    def sizeof_fmt(this, num, suffix="B"):
        for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"