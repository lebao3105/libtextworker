# 	A cross-platform library for Python apps.
# 	Copyright (C) 2023 Le Bao Nguyen and contributors.
# 	This is a part of the libtextworker project.
# 	Licensed under the GNU General Public License version 3.0 or later.

import os
import time
import wx
import wx.lib.newevent

from enum import auto
from libtextworker.general import CraftItems, libTewException
from libtextworker.interface.base.dirctrl import *
from typing import Callable
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

# Index for images (for nodes)

imgs = wx.ImageList(16, 16) # TODO

def addImg(name: str) -> int:
    return imgs.Add(
        wx.ArtProvider.GetBitmap(
            getattr(wx, f"ART_{name.upper()}"), wx.ART_OTHER, (16, 16)
        )
    )

folderidx = addImg("folder")
fileidx = addImg("normal_file")
openfolderidx = addImg("folder_open")

# File system events
# I leave them here and you just do what you want
# Each *Event class here (yeah they are classes) accepts path as the main keyword.
# Use: wx.PostEvent(target, *Event(path=event.src_path)) with event is a watchdog's FileSystemEvent object
FileEditedEvent, EVT_FILE_EDITED = wx.lib.newevent.NewEvent()
FileCreatedEvent, EVT_FILE_CREATED = wx.lib.newevent.NewEvent()
FileDeletedEvent, EVT_FILE_DELETED = wx.lib.newevent.NewEvent()
FileOpenedEvent, EVT_FILE_OPEN = wx.lib.newevent.NewEvent()
FileClosedEvent, EVT_FILE_CLOSED = wx.lib.newevent.NewEvent()
FileMovedEvent, EVT_FILE_MOVED = wx.lib.newevent.NewEvent()

DirEditedEvent, EVT_DIR_EDITED = wx.lib.newevent.NewEvent()
DirCreatedEvent, EVT_DIR_CREATED = wx.lib.newevent.NewEvent()
DirMovedEvent, EVT_DIR_MOVED = wx.lib.newevent.NewEvent()
DirDeletedEvent, EVT_DIR_DELETED = wx.lib.newevent.NewEvent()

class FSEventHandler(FileSystemEventHandler):
    """
    A file system event handler derived from watchdog's FileSystemEventHandler.

    On both wx and Tk, a new event will be generated.
    Set the Target attribute which the handler sends the event to.

    Or, if you use this for your own widget, derive this class like any other classes
    you use for that widget, and set TargetIsSelf = True instead of Target.
    This class does not use __init__.

    Currently only one target is supported.

    Example usage:
    ```python
        from watchdog.observers import Observer
        (...)

        def on_close(evt): # On window close
            observer.stop()
            observer.join()
            evt.Skip()

        def func(evt):
            # Do anything with evt.path!

        wind = wx.(...) # A wxWindow
        wind.Bind("put your wanted event here", func)
        path = os.path.expanduser('~/')
        evt_handler = FSEventHandler()
        evt_handler.Target = wind
        observer = Observer()
        observer.schedule(evt_handler, path, recursive=True)
        observer.start()
    ```
    """

    Target: wx.Window
    TargetIsSelf: bool = True

    def evtIsDir(this, event: FileSystemEvent): return "Dir" if event.is_directory else "File"
    def getTarget(this): return this.Target if not this.TargetIsSelf else this

    # It sucks when I can't use __dict__ (module variable) to access
    # class easier (= less code used)

    def on_moved(this, event: FileSystemEvent): 
        if this.evtIsDir(event) == "Dir": cls_to_use = DirMovedEvent
        else: cls_to_use = FileMovedEvent
        wx.PostEvent(this.getTarget(), cls_to_use(path=event.src_path))

    def on_created(this, event: FileSystemEvent): 
        if this.evtIsDir(event) == "Dir": cls_to_use = DirCreatedEvent
        else: cls_to_use = FileCreatedEvent
        wx.PostEvent(this.getTarget(), cls_to_use(path=event.src_path))

    def on_deleted(this, event: FileSystemEvent):
        if this.evtIsDir(event) == "Dir": cls_to_use = DirDeletedEvent
        else: cls_to_use = FileDeletedEvent
        wx.PostEvent(this.getTarget(), cls_to_use(path=event.src_path))

    def on_modified(this, event: FileSystemEvent): 
        if this.evtIsDir(event) == "Dir": cls_to_use = DirEditedEvent
        else: cls_to_use = FileEditedEvent
        wx.PostEvent(this.getTarget(), cls_to_use(path=event.src_path))

    def on_closed(this, event: FileSystemEvent): 
        wx.PostEvent(this.getTarget(), FileClosedEvent(path=event.src_path))

    def on_opened(this, event: FileSystemEvent): 
        wx.PostEvent(this.getTarget(), FileOpenedEvent(path=event.src_path))

# For the old os.walk method, please head to
# https://python-forum.io/thread-8513.html

class DirCtrl(wx.TreeCtrl, FSEventHandler, DirCtrlBase):
    """
    A directory list made from wxTreeCtrl.
    This is WIP, and lacks lots of features:
    * Label editting
    * Copy-paste + right-click menu
    * Drag-n-drop
    * Hidden files detect (quite hard, may need to use C/C++)
    * Sorting items

    Flags available:
    * DC_EDIT = wx.TR_EDIT_LABELS
    * DC_HIDEROOT = hide the root node
    * DC_ONEROOT: only use one root node
    * DC_MULTIPLE = wx.TR_MULTIPLE (multiple selections)
    * No flag at all = wx.TR_DEFAULT_STYLE

    If you want to add more than one folder to this control,
    use DC_HIDEROOT and disable DC_ONEROOT (default).
    """

    Parent_ArgName = "parent"
    TargetIsSelf = True
    Observers: dict[str] = {}

    def __init__(this, *args, **kw):
        args, kw = DirCtrlBase.__init__(this, *args, **kw)

        # Process custom styles
        if not "style" in kw:
            # wx doc about wxTR_DEFAULT_STYLE:
            # set flags that are closet to the native system's defaults.
            if not len(args) >= 5:
                styles = wx.TR_DEFAULT_STYLE #| wx.TR_HIDE_ROOT
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
            if not DC_ONEROOT in this.Styles: # = use multiple folders
                styles |= wx.TR_HIDE_ROOT
            # else:
                # should throw a warning here, but iamlazy rn

        if DC_MULTIPLE in this.Styles:
            styles |= wx.TR_MULTIPLE

        if use_args:
            args[4] = styles
        else:
            kw["style"] = styles

        wx.TreeCtrl.__init__(this, *args, **kw)
        this.AssignImageList(imgs)
        this.Bind(wx.EVT_TREE_SEL_CHANGED, this.LazyExpand)

        def AddItem(evt: FileCreatedEvent | DirCreatedEvent):
            this.AppendItem(this.MatchItem(os.path.dirname(evt.path)),
                            os.path.basename(evt.path),
                            fileidx if isinstance(evt, FileCreatedEvent) else folderidx)
            evt.Skip()
        
        def DeleteItem(evt: FileDeletedEvent | DirDeletedEvent):
            wx.TreeCtrl.Delete(this, this.MatchItem(evt.path))
            evt.Skip()

        this.Bind(EVT_FILE_CREATED, AddItem)
        this.Bind(EVT_DIR_CREATED, AddItem)
        this.Bind(EVT_FILE_DELETED, DeleteItem)
        this.Bind(EVT_DIR_DELETED, DeleteItem)
    
    def Destroy(this):
        if this.Observers:
            for item in this.Observers:
                this.Observers[item].stop()
                this.Observers[item].join()
            del this.Observers
        return wx.TreeCtrl.Destroy(this)

    def __del__(this): return this.Destroy()

    def LazyExpand(this, what: wx.PyEvent | wx.TreeItemId):
        """
        Expand the given/currently selected item.

        Explain: if the target item has childs inside, that means
        the item has been opened before. This can be done by checking
        whether the item full path is a directory and has items inside.
        """
        if isinstance(what, wx.TreeItemId):
            path = what
        else:
            path = this.GetSelection()

        fullpath = os.path.normpath(this.GetFullPath(path))

        if os.path.isdir(fullpath) and this.ItemHasChildren(path):
            wx.TreeCtrl.DeleteChildren(this, path)
            this.SetItemImage(path, openfolderidx, wx.TreeItemIcon_Expanded)
            ls = os.listdir(fullpath)
            for item in ls:
                craftedpath = CraftItems(fullpath, item)
                if os.path.isfile(craftedpath) and DC_DIRONLY in this.Styles:
                    continue
                icon = folderidx if os.path.isdir(craftedpath) else fileidx

                newitem = this.AppendItem(path, item, icon)

                if os.path.isdir(craftedpath) and len(os.listdir(craftedpath) >= 1):
                    this.SetItemHasChildren(newitem)
        
        if isinstance(what, wx.PyEvent):
            what.Skip()

    def SetFolder(this, path: str):
        """
        Make DirCtrl to open (a) directory.
        @param path (str): Target path
        @since 0.1.4: Code description
        """

        DirCtrlBase.SetFolder(this, path, False)

        if not DC_ONEROOT in this.Styles and DC_HIDEROOT in this.Styles:
            root = this.GetRootItem()
            if not root: root = this.AddRoot("Hidden root"); kickstart = None
            else:
                # From SO - legit
                # Check if there was a "child" node for the target directory
                def iterate_root():
                    item, cookie = this.GetFirstChild(root)
                    while item.IsOk():
                        if this.GetItemText(item) == path:
                            return item
                        item, cookie = this.GetNextChild(root, cookie)
        
                kickstart = iterate_root()
            if not kickstart: kickstart = this.AppendItem(root, path)

        elif DC_ONEROOT in this.Styles:
            this.DeleteAllItems()
            kickstart = this.AddRoot(path)
        else:
            raise libTewException("The tree cannot determine whether to delete everything"
                                  " and start from scratch or just add a new one while keeping"
                                  " the old root node. Ask the app developer for this.")

        this.SetItemHasChildren(kickstart)
        this.Observers[path] = Observer()
        this.Observers[path].schedule(this, path, recursive=True)
        this.Observers[path].start()

    # From SO (that iterate_root function above) and the
    # help of Google Bard (and I found the problem myself,
    # Bard just use one more while loop and that's all, 
    # cannot go deeper of the tree)
    def MatchItem(this, path: str, start: wx.TreeItemId | None = None) -> wx.TreeItemId:
        """
        Find for an item in the tree by the specified path.
        "Item" here is a wx.TreeItemId object.
        """
        parent = this.GetRootItem() if not start else start
        item, cookie = this.GetFirstChild(parent)
        while item.IsOk():
            if this.GetFullPath(item) == path:
                return item
            if this.ItemHasChildren(item):
                check = this.MatchItem(path, item)
                if check: return check
            item, cookie = this.GetNextChild(parent, cookie)

    def GetNodeChildren(this, item: wx.TreeItemId | str) -> list[wx.TreeItemId]:
        """
        Get all subitems of a tree node.
        """

        if isinstance(item, str):
            node = this.MatchItem(item)
        else:
            node = item
        result = []
        it, cookie = this.GetFirstChild(node)
        while it.IsOk():
            result += [it]
            it, cookie = this.GetNextChild(it, cookie)
        return result

    def Delete(this, item: wx.TreeItemId):
        """
        Delete the specified item, but also delete the item on the
        file system.
        wx.TreeCtrl.Delete() exists (original method, use with care).
        """
        fullpath = this.GetFullPath(item)
        if os.path.isdir(fullpath) and fullpath in this.Observers:
            this.Observers[fullpath].stop()
            this.Observers[fullpath].join()
            this.Observers.pop(fullpath)
        import shutil
        if os.path.isdir(fullpath): shutil.rmtree(fullpath)
        else: os.remove(fullpath)
        wx.TreeCtrl.Delete(this, item)
    
    def DeleteChildren(this, item: wx.TreeItemId):
        """
        Remove all subitems of the specified item, except the item itself.
        Also remove them from the file system.
        wx.TreeCtrl.DeleteChildren() exists (original method, use with care).
        """
        if not this.ItemHasChildren(item): return
        for child in this.GetNodeChildren(item):
            this.Delete(child)

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
                if DC_HIDEROOT in this.Styles and DC_ONEROOT not in this.Styles and parent in this.GetNodeChildren(this.GetRootItem()): return
                parent = this.GetItemParent(parent)
                getroot()

        getroot()

        if len(result) >= 2:
            return CraftItems(*tuple(result))
        else:
            return result[0]


# @since 0.1.4: PatchedDirCtrl renamed to DirCtrl, and PatchedDirCtrl now points to that class
# @brief "Patched".. seems not right:v (it's derived from wxTreeCtrl not wxGenericDirCtrl)
PatchedDirCtrl = DirCtrl


class DirList(wx.ListCtrl, FSEventHandler, DirCtrlBase):
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
    Styles = DC_USEICON
    History: list = []
    TargetIsSelf = True
    Watcher: Observer

    def __init__(
        this,
        parent: wx.Window,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.LC_REPORT,
        validator=wx.DefaultValidator,
        name=wx.ListCtrlNameStr,
        w_styles: auto = DC_USEICON,
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

    def Destroy(this):
        this.Watcher.stop()
        this.Watcher.join()
        del this.Watcher
        wx.ListCtrl.Destroy(this)
    
    def __del__(this): return this.Destroy()

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
        this.Watcher = Observer()
        this.Watcher.schedule(this, path, True)
        this.Watcher.start()
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
