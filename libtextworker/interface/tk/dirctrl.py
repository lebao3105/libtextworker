import os

from tkinter import TclError, ttk
from libtextworker.general import CraftItems
from libtextworker.interface.base.dirctrl import DirCtrlBase

class DirCtrl(ttk.Treeview, DirCtrlBase):

    Parent_ArgName = "master"
    _Frame = ttk.Frame

    def __init__(self, *args, **kwds):
        """
        A ttkTreeview customized to show folder list using os.listdir.
        Multiple roots is supported, but only adding new for now.
        Lacks label editing, DND, right-click menu, item icon.

        DirCtrl's custom styles can be defined via the "dc_styles" keyword.
        """
        args, kwds = DirCtrlBase.__init__(self, *args, **kwds)
        ttk.Treeview.__init__(self, self.Frame, *args, **kwds)

        ysb = ttk.Scrollbar(self.Frame, orient="vertical", command=self.yview)
        xsb = ttk.Scrollbar(self.Frame, orient="horizontal", command=self.xview)
        self.configure(yscroll=ysb.set, xscroll=xsb.set)

        self.pack(expand=True, fill="both")
        ysb.pack(fill="y", expand=True)
        xsb.pack(fill="x", expand=True)

    def SetFolder(self, path: str, newroot: bool = False):

        def insert_node(node: str, folderpath: str):
            for item in os.listdir(folderpath):
                # craftedpath = CraftItems(fullpath, item)
                new = self.insert(node, "end", text=item, open=False)
                if os.path.isdir(os.path.join(folderpath, item)):
                    self.insert(new, "end")

        # "Lazy" expand
        # Only load the folder content when the user open

        def Expand(evt):
            path = self.focus()
            self.item(path, open=True)
            fullpath = os.path.normpath(self.GetFullPath())
            iter = os.listdir(fullpath)

            if len(iter) == 0: return
            try:
                self.delete(self.get_children(path))
            except TclError:
                pass

            insert_node(path, fullpath)
        
        DirCtrlBase.SetFolder(self, path, newroot)
        
        first = self.insert("", "end", text=path)
        insert_node(first, path)

        self.bind("<<TreeviewOpen>>", Expand)


    def GetFullPath(self, item: str | None = None) -> str:

        # Like wx, ttkTreeView handles items by IDs
        if not item:
            item = self.focus()

        parent = self.parent(item)
        node = []

        def getroot():
            nonlocal parent
            text = self.item(parent, 'text')
            node.append(text)
            if parent != "":
                parent = self.parent(parent)
                getroot()

        getroot()
        node.pop()
        node.reverse()
        print(node)

        return CraftItems(*tuple(node), self.item(item, "text"))
