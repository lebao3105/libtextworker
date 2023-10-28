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

from tkinter import TclError, ttk
from libtextworker.general import CraftItems
from libtextworker.interface.base.dirctrl import DC_DIRONLY, DirCtrlBase


class DirCtrl(ttk.Treeview, DirCtrlBase):
    Parent_ArgName = "master"
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
