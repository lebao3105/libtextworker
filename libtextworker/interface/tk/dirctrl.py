"""
@package libtextworker.interface.tk.dirctrl
@brief Directory tree for Tkinter
"""

# 	A cross-platform library for Python apps.
# 	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
# 	This is a part of the libtextworker project.
# 	Licensed under the GNU General Public License version 3.0 or later.

import os
import time

from tkinter import ttk, Misc
from warnings import warn

from libtextworker.interface.tk import TK_PLACEOPTS, TK_USEGRID, TK_USEPACK

from ..base.dirctrl import *
from ... import _
from ...general import CraftItems, Importable

if Importable["watchdog"]:
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer

    class FSEventHandler(FileSystemEventHandler):
        """
        A file system events handler derived from watchdog's FileSystemEventHandler.

        On both wx and Tk, a new event will be generated.
        Set the Target attribute which the handler sends the event to.

        On Tk, since a new event is just a new event: no custom value allowed. However
        you can do a bind_class to connect the event to all widgets with your specified
        class:
        
            ```python
            # Binds FileDeletedEvent to all StyledTextControl instances
            root.bind_class('StyledTextControl', FileDeletedEvent, callback)
            # Or this (add=True won't replace the current callback if any)
            widget.bind(FileDeletedEvent, callback, add=True)
            ```

        Or, if you use this for your own widget, derive this class like any other classes
        you use for that widget, and set TargetIsSelf = True instead of Target.
        This class does not use __init__.

        Currently only one target is supported. You need to do something else to handle the
        events generated here.
        """

        Target: Misc
        TargetIsSelf: bool

        def evtIsDir(this, event: FileSystemEvent): return "Dir" if event.is_directory else "File"
        def getTarget(this): return this.Target if not this.TargetIsSelf else this
        
        def on_moved(this, event: FileSystemEvent):
            if this.evtIsDir(event) == "Dir": what_to_use = DirMovedEvent
            else: what_to_use = FileMovedEvent
            this.getTarget().event_generate(what_to_use, data=event.src_path)

        def on_created(this, event: FileSystemEvent): 
            if this.evtIsDir(event) == "Dir": what_to_use = DirCreatedEvent
            else: what_to_use = FileCreatedEvent
            this.getTarget().event_generate(what_to_use, data=event.src_path)

        def on_deleted(this, event: FileSystemEvent):
            if this.evtIsDir(event) == "Dir": what_to_use = DirDeletedEvent
            else: what_to_use = FileDeletedEvent
            this.getTarget().event_generate(what_to_use, data=event.src_path)

        def on_modified(this, event: FileSystemEvent): 
            if this.evtIsDir(event) == "Dir": what_to_use = DirEditedEvent
            else: what_to_use = FileEditedEvent
            this.getTarget().event_generate(what_to_use, data=event.src_path)

        def on_closed(this, event: FileSystemEvent): 
            this.getTarget().event_generate(FileClosedEvent, data=event.src_path)

        def on_opened(this, event: FileSystemEvent): 
            this.getTarget().event_generate(FileOpenedEvent, data=event.src_path)
else:
    class FSEventHandler:
        pass

# File system events
# I leave them here and you just do what you want to

FileEditedEvent = "<<FileEdited>>"
FileCreatedEvent = "<<FileCreated>>"
FileDeletedEvent = "<<FileDeleted>>"
FileOpenedEvent = "<<FileOpened>>"
FileClosedEvent = "<<FileClosed>>"
FileMovedEvent = "<<FileMoved>>"

DirEditedEvent = "<<DirEdited>>"
DirCreatedEvent = "<<DirCreated>>"
DirMovedEvent = "<<DirMoved>>"
DirDeletedEvent = "<<DirDeleted>>"

class DirCtrl(ttk.Treeview, FSEventHandler, DirCtrlBase):
    watchChanges: bool

    TargetIsSelf = True
    Parent_ArgName = "master"
    _Frame = ttk.Frame

    def __init__(this, master: Misc, refresh_on_changes: bool,
                 place_options: TK_PLACEOPTS = TK_USEPACK, *args, **kwds):
        """
        A ttkTreeview customized to show folder list using os.listdir.
        Multiple roots is supported, but only adding new for now.
        Lacks label editing, DND, right-click menu, item icon.

        DirCtrl's custom styles can be defined via the "w_styles" keyword.
        """

        args, kwds = DirCtrlBase.__init__(this, master, *args, **kwds)
        ttk.Treeview.__init__(this, this.Frame, *args, **kwds)

        ysb = ttk.Scrollbar(this.Frame, orient="vertical", command=this.yview)
        xsb = ttk.Scrollbar(this.Frame, orient="horizontal", command=this.xview)
        this.configure(yscroll=ysb.set, xscroll=xsb.set)

        if TK_USEPACK in place_options:
            ysb.pack(fill="y", expand=False, side="right")
            xsb.pack(fill="x", expand=False, side="bottom")
            this.pack(expand=True, fill="both")
        elif TK_USEGRID in place_options:
            ysb.grid(column=1, row=0, sticky="ns")
            xsb.grid(column=0, row=1, sticky="ew")
            this.grid(column=0, row=0)
        else:
            raise NotImplementedError("If you want to use TK_USEPLACE, then sorry it is not used here (not implemented)."
                                      "A widget place method is required (TK_USEPACK or TK_USEGRID).")

        if refresh_on_changes:
            if Importable["watchdog"]:
                this.Observers: dict[str, Observer] = {}
                this.watchChanges = refresh_on_changes
            else:
                warn('Setting up DirCtrl has a warning, about missing dependency for watching file system changes (watchdog)')
                this.watchChanges = False

        this.bind("<<TreeviewOpen>>", this.Expand)

    def destroy(this):
        if this.Observers:
            for key in this.Observers:
                this.Observers[key].stop()
                this.Observers[key].join()
            this.Observers.clear()

        ttk.Treeview.destroy(this)

    def Expand(this, evt = None, path: str | None = None):
        """
        Expands a node.

        This can be called manually by setting the path parameter, or \
            bind with a node expand event (<<TreeViewOpen>>), which is \
            bond by default by DirCtrl.
        
        Quits silently when the specified path is invalid, or no item on focus.
        """

        if path is None: path = this.focus()
        if not path: return

        this.item(path, open=True)
        
        this._insert_node(path, os.path.normpath(this.GetFullPath(path)))

    def _insert_node(this, node: str, folderpath: str):
        """
        Internal function to insert childrens into a node.
        """
        
        items = os.listdir(folderpath)

        if len(items) > 0:
            try:
                if childs := this.get_children(node):
                    if len(childs) > 0:
                        if this.watchChanges:
                            this.delete(*childs)
                        else:
                            first_child = childs[0]
                            if not this.item(first_child, 'text'): this.delete(first_child)
                            else: return
            except:
                pass

            for item in os.listdir(folderpath):
                new = this.insert(node, "end", text=item, open=False)

                # Nothing else that marks a node as expandable
                # than making an empty item
                if os.path.isdir(os.path.join(folderpath, item)):
                    this.insert(new, "end")

    def SetFolder(this, path: str, newroot: bool = False):
        """
        Sets/add a new folder to the tree.
        """

        DirCtrlBase.SetFolder(this, path, newroot)

        first = this.insert("", "end", text=path)
        this._insert_node(first, path)

        if Importable["watchdog"]:
            this.Observers[path] = Observer()
            this.Observers[path].schedule(this, path, recursive=True)
            this.Observers[path].start()

    def GetFullPath(this, item: str | None = None) -> str | None:
        """
        Gets the full path of an item. If not specified: the on-focus item.
        
        Returns None if not able to.
        """

        # Like wx, ttkTreeView handles items by IDs
        if not item:
            item = this.focus()

        parent = this.parent(item)
        node = []

        def getroot():
            nonlocal parent
            text = this.item(parent, "text")
            node.append(text)
            if parent != "":
                parent = this.parent(parent)
                getroot()

        getroot()
        node.pop()
        node.reverse()
        # print(node)

        if node:
            return CraftItems(*tuple(node), this.item(item, "text"))


class DirList(ttk.Treeview, DirCtrlBase):
    Parent_ArgName = "master"
    _Frame = ttk.Frame

    def __init__(this, master: Misc, place_options: TK_PLACEOPTS = TK_USEPACK, *args, **kwds):
        """
        A directory items list.
        By default contains these columns:
        * Name
        * Item type (file, folder)
        * Last modified time
        * Item size
        Navigate history support. Not much customizable for now.
        No libtextworker custom style support for now.
        """

        args, kwds = DirCtrlBase.__init__(this, master, *args, **kwds)
        ttk.Treeview.__init__(this, this.Frame, show="headings",
                              columns = [ _("Name"), _("Item type"), _("Last modified"), _("Size") ],
                              *args, **kwds)

        ysb = ttk.Scrollbar(this.Frame, orient="vertical", command=this.yview)
        xsb = ttk.Scrollbar(this.Frame, orient="horizontal", command=this.xview)
        this.configure(yscroll=ysb.set, xscroll=xsb.set)

        if TK_USEPACK in place_options:
            ysb.pack(fill="y", expand=True, side="right")
            xsb.pack(fill="x", expand=True, side="bottom")
            this.pack(expand=True, fill="both")
        elif TK_USEGRID in place_options:
            this.grid(column=0, row=0, sticky="nsew")
            ysb.grid(column=1, row=0, sticky="nse")
            xsb.grid(column=0, row=1, sticky="ews")
        else:
            raise NotImplementedError("If you want to use TK_USEPLACE, then sorry it is not used here (not implemented)."
                                      "A widget place method is required (TK_USEPACK or TK_USEGRID).")

    def SetFolder(this, path: str):
        """
        Navigate to the specified folder.
        """

        DirCtrlBase.SetFolder(this, path, False)
        this.delete(*this.get_children())

        for it in os.listdir(path):
            fullpath = os.path.join(path, it)
            statinfo = os.stat(fullpath)

            if os.path.isdir(os.path.join(path, it)):
                it_type = _("Folder")
                it_size = ""
            elif DC_DIRONLY not in this.Styles:
                it_type = _("File")
                it_size = this.sizeof_fmt(statinfo.st_size)

            lastmod = time.strftime("%d %b %Y, %H:%M:%S", time.localtime(statinfo.st_mtime))

            this.insert("", "end", values=(it, it_type, lastmod, it_size))
