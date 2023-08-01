import os
import wx

# from jaraco.path import
from libtextworker.general import CraftItems


# Referenced from https://python-forum.io/thread-8513.html
class DirCtrl(wx.TreeCtrl):
    """
    A directory list made from wxTreeCtrl.
    This is WIP, and lacks lots of features:
    * Label editting
    * Copy-paste + right-click menu
    * Drag-n-drop
    * Hidden files detect (quite hard, may need to use C/C++)
    """

    nodes: dict

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        imgs = wx.ImageList(16, 16)
        self.folderidx = imgs.Add(
            wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16))
        )
        self.fileidx = imgs.Add(
            wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16))
        )

        # Extras - opening folder icon
        # Bind_ed with wxEVT_TREE_ITEM_EXPANDED event
        self.openfolder = imgs.Add(
            wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, (16, 16))
        )

        self.AssignImageList(imgs)

    def SetFolder(self, path: str, newroot: bool = False):
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

            path = self.GetSelection()
            fullpath = os.path.abspath(self.GetFullPath(path))
            self.SetItemImage(path, self.openfolder, wx.TreeItemIcon_Expanded)
            
            if len(os.listdir(fullpath)) == 0: self.SetItemHasChildren(path, False); return
            # ^ blank folder? Get out eventually

            for item in os.listdir(fullpath):
                craftedpath = CraftItems(fullpath, item)
                icon = self.folderidx if os.path.isdir(craftedpath) else self.fileidx

                self.nodes[craftedpath] = self.AppendItem(path, item, icon)

                if os.path.isdir(craftedpath):
                    self.SetItemHasChildren(self.nodes[craftedpath])
        
        path = os.path.normpath(path)
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Directory not found or is a file: {path}")

        if self.GetRootItem() and not newroot:
            self.DeleteAllItems()

        self.nodes = {path: self.AddRoot(path, self.folderidx)}
        self.SetItemHasChildren(self.nodes[path])
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, Expand)

    def GetFullPath(self, item: wx.TreeItemId | None = None) -> str:
        """
        Get the full path of an item.
        """
        if item == None:
            parent = self.GetSelection()
        else:
            parent = item

        result = []

        if parent == self.GetRootItem():
            return self.GetItemText(parent)

        def getroot():
            nonlocal parent
            text = self.GetItemText(parent)
            result.append(text)
            if parent != self.GetRootItem():
                parent = self.GetItemParent(parent)
                getroot()

        getroot()
        result.reverse()

        return CraftItems(*tuple(result))

# @since 0.1.4: PatchedDirCtrl renamed to DirCtrl, and PatchedDirCtrl now points to that class
# @brief "Patched".. seems not right:v (it's derived from wxTreeCtrl not wxGenericDirCtrl)
PatchedDirCtrl = DirCtrl