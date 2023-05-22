import wx
import jaraco.path

# Referenced from https://python-forum.io/thread-8513.html
class PatchedDirCtrl(wx.TreeCtrl):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        imgs = wx.ImageList(16, 16)
        self.folderidx = imgs.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        self.fileidx = imgs.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))
        
        # Extras - opening folder icon
        # Bind_ed with wxEVT_TREE_ITEM_EXPANDED event
        self.openfolder = imgs.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, (16,16)))

        self.AssignImageList(imgs)
    
    def SetFolder(self, path: str, showhidden: bool = True):
        import os, stat

        if not os.path.isdir(path):
            raise Exception("PatchedDirCtrl-Directory not found: " + path)

        ids = {path: self.AddRoot(path, self.folderidx)}
        self.SetItemHasChildren(ids[path])
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.SetItemImage(ids[path], self.openfolder, wx.TreeItemIcon_Expanded))

        for dirpath, dirnames, filenames in os.walk(path):

            for dirname in sorted(dirnames):
                fullpath = os.path.join(dirpath, dirname)
                ids[fullpath] = self.AppendItem(ids[dirpath], dirname, self.folderidx)
                if showhidden == False and jaraco.path.is_hidden(fullpath):
                    self.Delete(ids[fullpath])
                    break
                self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.SetItemImage(ids[fullpath], self.openfolder, wx.TreeItemIcon_Expanded))
            
            for filename in sorted(filenames):
                item = self.AppendItem(ids[dirpath], filename, self.fileidx)
                if showhidden == False and jaraco.path.is_hidden(os.path.join(dirpath, filename)):
                    self.Delete(item)
                    break
    