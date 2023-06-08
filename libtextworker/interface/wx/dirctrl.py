import os
import wx

# from jaraco.path import
from libtextworker.general import CraftItems


# Referenced from https://python-forum.io/thread-8513.html
class PatchedDirCtrl(wx.TreeCtrl):
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

    def SetFolder(self, path: str, showhidden: bool = True):
        if not os.path.isdir(path):
            raise Exception("PatchedDirCtrl-Directory not found: " + path)

        if self.GetRootItem():
            self.DeleteAllItems()

        ids = {path: self.AddRoot(path, self.folderidx)}
        self.SetItemHasChildren(ids[path])
        self.Bind(
            wx.EVT_TREE_ITEM_EXPANDED,
            self.SetItemImage(ids[path], self.openfolder, wx.TreeItemIcon_Expanded),
        )

        for dirpath, dirnames, filenames in os.walk(path):
            if not dirpath in ids:
                break

            # if not showhidden:
            #     dirnames = [d for d in dirnames if not is_hidden(os.path.join(dirpath, d))]

            # if showhidden == False and is_hidden(dirpath):
            #     continue

            for dirname in sorted(dirnames):
                fullpath = os.path.join(dirpath, dirname)

                ids[fullpath] = self.AppendItem(ids[dirpath], dirname, self.folderidx)
                self.Bind(
                    wx.EVT_TREE_ITEM_EXPANDED,
                    self.SetItemImage(
                        ids[fullpath], self.openfolder, wx.TreeItemIcon_Expanded
                    ),
                )

            # if not showhidden:
            #     filenames = [f for f in filenames if not is_hidden(os.path.join(dirpath, f))]

            for filename in sorted(filenames):
                self.AppendItem(ids[dirpath], filename, self.fileidx)

    def GetFullPath(self, item: wx.TreeItemId | None = None):
        if item == None:
            parent = self.GetSelection()
        else:
            parent = item

        result = []

        while self.GetItemParent(parent):
            text = self.GetItemText(parent)
            result.append(text)
            parent = self.GetItemParent(parent)

        result.reverse()

        return CraftItems(*tuple(result))
