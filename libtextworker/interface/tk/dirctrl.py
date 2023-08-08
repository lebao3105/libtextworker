import os
import tkinter.ttk as ttk

from libtextworker.general import CraftItems


class DirCtrl(ttk.Treeview):
    """
    A ttkTreeview customized to show folder list using os.listdir.
    Multiple roots is supported, but only adding new for now.
    Lacks label editing, DND, right-click menu.
    """

    nodes: dict

    def __init__(self, **kwds):
        self._frame = ttk.Frame(kwds.get("master", None))
        super().__init__(self._frame, **kwds)

        ysb = ttk.Scrollbar(self._frame, orient="vertical", command=self.yview)
        xsb = ttk.Scrollbar(self._frame, orient="horizontal", command=self.xview)
        self.configure(yscroll=ysb.set, xscroll=xsb.set)

        ysb.pack(fill="y", expand=True)
        xsb.pack(fill="x", expand=True)
        self.pack(expand=True, fill="both")

    def SetFolder(self, path: str, newroot: bool = False):
        """
        Make DirCtrl to show a new folder tree.
        @param path (str): Target path
        @param newroot (bool): Whatever to create a new root or not (delete all previous roots if any)
        """

        # "Lazy" expand
        # Only load the folder content when the user open

        def Expand(evt):
            path = self.focus()
            fullpath = os.path.normpath(self.GetFullPath(path))

    def GetFullPath(self, item: str | None = None) -> str:
        """
        Get the full path of an item/current selected item if @item parameter is not specified.
        """

        # Like wx, ttkTreeView handles items by IDs
        if not item:
            item = self.selection()[0]

        parent = self.parent(item)
        node = []

        while parent != "":  # Jump upper one level until we can't (root)
            node.append(self.item(parent)["text"])
            parent = self.parent(parent)

        node.reverse()
        return CraftItems(*tuple(node), self.item(item, "text"))
