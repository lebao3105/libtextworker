# 	A cross-platform library for Python apps.
# 	Copyright (C) 2023 Le Bao Nguyen and contributors.
# 	This is a part of the libtextworker project.
# 	Licensed under the GNU General Public License version 3.0 or later.

"""
@package libtextworker.interface.tk.dirctrl
@brief Directory tree for Tkinter
"""
import os
import time

from tkinter import TclError, ttk, Misc
from libtextworker.general import CraftItems
from libtextworker.interface.base.dirctrl import *
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

# File system events
# I leave them here and you just do what you want
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

    # It sucks when I can't use __dict__ (module variable) to access
    # class easier (= less code used)

    def on_moved(this, event: FileSystemEvent):
        if this.evtIsDir(event) == "Dir": what_to_use = DirMovedEvent
        else: what_to_use = FileMovedEvent
        this.getTarget().event_generate(what_to_use, path=event.src_path)

    def on_created(this, event: FileSystemEvent): 
        if this.evtIsDir(event) == "Dir": what_to_use = DirCreatedEvent
        else: what_to_use = FileCreatedEvent
        this.getTarget().event_generate(what_to_use, path=event.src_path)

    def on_deleted(this, event: FileSystemEvent):
        if this.evtIsDir(event) == "Dir": what_to_use = DirDeletedEvent
        else: what_to_use = FileDeletedEvent
        this.getTarget().event_generate(what_to_use, path=event.src_path)

    def on_modified(this, event: FileSystemEvent): 
        if this.evtIsDir(event) == "Dir": what_to_use = DirEditedEvent
        else: what_to_use = FileEditedEvent
        this.getTarget().event_generate(what_to_use, path=event.src_path)

    def on_closed(this, event: FileSystemEvent): 
        this.getTarget().event_generate(FileClosedEvent, path=event.src_path)

    def on_opened(this, event: FileSystemEvent): 
        this.getTarget().event_generate(FileOpenedEvent, path=event.src_path)

class DirCtrl(ttk.Treeview, FSEventHandler, DirCtrlBase):
    Parent_ArgName = "master"
    TargetIsSelf = True
    Observers: dict[str, Observer] = {}
    _Frame = ttk.Frame

    def __init__(this, *args, **kwds):
        """
        A ttkTreeview customized to show folder list using os.listdir.
        Multiple roots is supported, but only adding new for now.
        Lacks label editing, DND, right-click menu, item icon.

        DirCtrl's custom styles can be defined via the "w_styles" keyword.
        """
        args, kwds = DirCtrlBase.__init__(this, *args, **kwds)
        ttk.Treeview.__init__(this, this.Frame, *args, **kwds)

        ysb = ttk.Scrollbar(this.Frame, orient="vertical", command=this.yview)
        xsb = ttk.Scrollbar(this.Frame, orient="horizontal", command=this.xview)
        this.configure(yscroll=ysb.set, xscroll=xsb.set)

        # ysb.pack(fill="y", expand=True, side="right")
        # xsb.pack(fill="x", expand=True, side="bottom")
        # this.pack(expand=True, fill="both")

        this.grid(column=0, row=0)
        ysb.grid(column=1, row=0, sticky="ns")
        xsb.grid(column=0, row=1, sticky="ew")

    def destroy(this):
        if this.Observers:
            for key in this.Observers:
                this.Observers[key].stop()
                this.Observers[key].join()
            del this.Observers
        ttk.Treeview.destroy(this)

    def SetFolder(this, path: str, newroot: bool = False):
        def insert_node(node: str, folderpath: str):
            for item in os.listdir(folderpath):
                # craftedpath = CraftItems(fullpath, item)
                new = this.insert(node, "end", text=item, open=False)
                if os.path.isdir(os.path.join(folderpath, item)):
                    this.insert(new, "end")

        # "Lazy" expand
        # Only load the folder content when the user open

        def Expand(evt):
            path = this.focus()
            this.item(path, open=True)
            fullpath = os.path.normpath(this.GetFullPath())
            iter = os.listdir(fullpath)

            if len(iter) == 0:
                return
            try:
                this.delete(this.get_children(path))
            except TclError:
                pass

            insert_node(path, fullpath)

        DirCtrlBase.SetFolder(this, path, newroot)

        first = this.insert("", "end", text=path)
        insert_node(first, path)

        this.Observers[path] = Observer()
        this.Observers[path].schedule(this, path, recursive=True)
        this.Observers[path].start()

        this.bind("<<TreeviewOpen>>", Expand)

    def GetFullPath(this, item: str | None = None) -> str:
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

    def __init__(this, *args, **kwds):
        args, kwds = DirCtrlBase.__init__(this, *args, **kwds)
        ttk.Treeview.__init__(
            this,
            this.Frame,
            columns=[_("Name"), _("Item type"), _("Last modified"), _("Size")],
            show="headings",
            *args,
            **kwds,
        )

        ysb = ttk.Scrollbar(this.Frame, orient="vertical", command=this.yview)
        xsb = ttk.Scrollbar(this.Frame, orient="horizontal", command=this.xview)
        this.configure(yscroll=ysb.set, xscroll=xsb.set)

        # ysb.pack(fill="y", expand=True, side="right")
        # xsb.pack(fill="x", expand=True, side="bottom")
        # this.pack(expand=True, fill="both")

        this.grid(column=0, row=0, sticky="nsew")
        ysb.grid(column=1, row=0, sticky="nse")
        xsb.grid(column=0, row=1, sticky="ews")

    def SetFolder(this, path: str):
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

            lastmod = time.strftime(
                "%d %b %Y, %H:%M:%S", time.localtime(statinfo.st_mtime)
            )

            this.insert("", "end", values=(it, it_type, lastmod, it_size))
