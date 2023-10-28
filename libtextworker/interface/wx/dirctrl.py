# 	A cross-platform library for Python apps.
# 	Copyright (C) 2023 Le Bao Nguyen and contributors.
# 	This is a part of the libtextworker project.
# 	Licensed under the GNU General Public License version 3.0 or later.

import os
import time
import wx

from enum import auto
from libtextworker.general import CraftItems
from libtextworker.interface.base.dirctrl import *
from typing import Callable

imgs = wx.ImageList(16, 16)


def addImg(name: str) -> int:
    return imgs.Add(
        wx.ArtProvider.GetBitmap(
            getattr(wx, f"ART_{name.upper()}"), wx.ART_OTHER, (16, 16)
        )
    )


folderidx = addImg("folder")
fileidx = addImg("normal_file")
openfolderidx = addImg("folder_open")

# For the old os.walk method, please head to
# https://python-forum.io/thread-8513.html


class DirCtrl(wx.TreeCtrl, DirCtrlBase):
    """
    A directory list made from wxTreeCtrl.
    This is WIP, and lacks lots of features:
    * Label editting
    * Copy-paste + right-click menu
    * Drag-n-drop
    * Hidden files detect (quite hard, may need to use C/C++)
    * Directory only
    """

    Parent_ArgName = "parent"

    def __init__(this, *args, **kw):
        args, kw = DirCtrlBase.__init__(this, *args, **kw)

        # Process custom styles
        if not "style" in kw:
            # wx doc about wxTR_DEFAULT_STYLE:
            # set flags that are closet to the native system's defaults.
            if not len(args) >= 5:
                styles = wx.TR_DEFAULT_STYLE
                use_args = False
            else:
                styles = args[4]
                use_args = True
        else:
            styles = kw["style"]
            use_args = False

        if DC_EDIT in this.Styles:
            styles |= wx.TR_EDIT_LABELS

        if DC_HIDEROOT in this.Styles:
            styles |= wx.TR_HIDE_ROOT

        if DC_MULTIPLE in this.Styles:
            styles |= wx.TR_MULTIPLE

        if use_args:
            args[4] = styles
        else:
            kw["style"] = styles

        wx.TreeCtrl.__init__(this, *args, **kw)
        this.AssignImageList(imgs)

    def SetFolder(this, path: str, newroot: bool = False):
        """
        Make DirCtrl to open (a) directory.
        @param path (str): Target path
        @param newroot (bool): Whatever to create a new root or not (incase we have >= premade root)
        @since 0.1.4: Code description + new param (newroot)
        """

        # "Lazy" expand
        # Why "lazy" here? Because this is called when we click an expandable item,
        # if it's not opened before, it will fill itself with new items.
        # else it will just show its (already) finished work.

        def Expand(evt):
            path = this.GetSelection()
            fullpath = os.path.normpath(this.GetFullPath(path))
            this.SetItemImage(path, this.openfolder, wx.TreeItemIcon_Expanded)

            if len(os.listdir(fullpath)) == 0:
                this.SetItemHasChildren(path, False)
                return
            # ^ blank folder? Get out eventually

            for item in os.listdir(fullpath):
                craftedpath = CraftItems(fullpath, item)
                if os.path.isfile(craftedpath) and DC_DIRONLY in this.Styles:
                    continue
                icon = folderidx if os.path.isdir(craftedpath) else fileidx

                newitem = this.AppendItem(path, item, icon)

                if os.path.isdir(craftedpath):
                    this.SetItemHasChildren(newitem)

        DirCtrlBase.SetFolder(this, path, newroot)

        kickstart = this.GetRootItem()

        if kickstart and not newroot:
            this.DeleteAllItems()

        elif this.GetItemText(kickstart) != path:
            kickstart = this.AddRoot(path, this.folderidx)

        this.SetItemHasChildren(kickstart)
        this.Bind(wx.EVT_TREE_ITEM_EXPANDED, Expand)

    def GetFullPath(this, item: wx.TreeItemId | None = None) -> str:
        """
        Get the full path of an item.
        The same work as wxGenericDirCtrl.GetPath.
        """
        if item == None:
            parent = this.GetSelection()
        else:
            parent = item

        result = []

        if parent == this.GetRootItem():
            return this.GetItemText(parent)

        def getroot():
            nonlocal parent
            text = this.GetItemText(parent)
            result.insert(0, text)
            if parent != this.GetRootItem():
                parent = this.GetItemParent(parent)
                getroot()

        getroot()
        # result.reverse()

        return CraftItems(*tuple(result))


# @since 0.1.4: PatchedDirCtrl renamed to DirCtrl, and PatchedDirCtrl now points to that class
# @brief "Patched".. seems not right:v (it's derived from wxTreeCtrl not wxGenericDirCtrl)
PatchedDirCtrl = DirCtrl


class DirList(wx.ListCtrl, DirCtrlBase):
    """
    Unlike wxDirCtrl, wxDirList lists not only files + folders, but also their
    last modified and item type, size. You will see it most in your file explorer,
    the main pane.
    Of couse this is wxLC_REPORT will be used.
    This comes with check buttons, which is optional.

    libtextworker flags to be ignored:
    * DC_HIDEROOT (where's the root node in this list control?)
    * DC_ONEROOT (one root by default so this is useless)
    """

    currpath: str
    Styles = DC_DYNAMIC | DC_USEICON
    History: list = []

    def __init__(
        this,
        parent: wx.Window,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.LC_REPORT,
        validator=wx.DefaultValidator,
        name=wx.ListCtrlNameStr,
        w_styles: auto = DC_DYNAMIC | DC_USEICON,
    ):
        if DC_EDIT in w_styles:
            style |= wx.LC_EDIT_LABELS

        for i in [wx.LC_ICON, wx.LC_SMALL_ICON, wx.LC_LIST]:
            if style & i:
                style /= i

        DirCtrlBase.__init__(this)
        wx.ListCtrl.__init__(this, parent, id, pos, size, style, validator, name)

        this.InsertColumn(0, _("Name"), width=246)
        this.InsertColumn(1, _("Item type"))
        this.InsertColumn(2, _("Last modified"), width=150)
        this.InsertColumn(3, _("Size"))

        this.AssignImageList(imgs, wx.IMAGE_LIST_SMALL)

        this.Bind(wx.EVT_LIST_ITEM_ACTIVATED, this.SetFolder)

    def DrawItems(this, path: str = os.path.expanduser("~/")):
        """
        Fill the list control with items;)
        """

        this.DeleteAllItems()
        for item in os.listdir(path):
            crafted = os.path.join(path, item)
            statinfo = os.stat(crafted)
            it_size = 0

            if os.path.isdir(crafted):
                it_size = ""
                this.InsertItem(0, item, folderidx)
                this.SetItem(0, 1, _("Folder"))
            elif DC_DIRONLY not in this.Styles:
                it_size = statinfo.st_size
                this.InsertItem(0, item, fileidx)
                this.SetItem(0, 1, _("File"))

            m_time = statinfo.st_mtime
            lastmod = time.strftime("%d %b %Y, %H:%M:%S", time.localtime(m_time))

            this.SetItem(0, 2, lastmod)

            if isinstance(it_size, int):
                it_size = this.sizeof_fmt(it_size)

            this.SetItem(0, 3, str(it_size))

    def SetFolder(this, evt=None, path: str = ""):
        """
        Make this control show the content of a folder.
        @param evt = None: wxListCtrl event
        @param path (str): Target path (if not specified but evt will use the current item instead)
        """
        if evt and not path:
            pos = evt.Index
            name = this.GetItemText(pos)
            item_type = this.GetItemText(pos, 1)

            if item_type == _("Folder"):
                path = os.path.join(this.currpath, name)
        elif not path:
            raise Exception(
                "Who the hell call DirList.GoDir with no directory to go???"
            )
        DirCtrlBase.SetFolder(this, path, False)
        this.DrawItems(path)
        this.PostSetDir(path, "go")

    def GoUp(this, evt):
        this.SetFolder(path=os.path.dirname(this.currpath))

    def GetFullPath(
        this, item: str | Callable | None = None, event: Callable | None = None
    ):
        """
        Never be implemented.
        Find the way yourself.
        """
        raise NotImplementedError("Why do you calling this? Don't be too lazy!")
