import os
import time
import wx

from libtextworker.general import CraftItems
from libtextworker.interface.base.dirctrl import DirCtrlBase

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

    def __init__(this, *args, **kw):
        args, kw = DirCtrlBase.__init__(this, *args, **kw)
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
                icon = folderidx if os.path.isdir(craftedpath) else fileidx

                newitem = this.AppendItem(path, item, icon)

                if os.path.isdir(craftedpath):
                    this.SetItemHasChildren(newitem)

        DirCtrlBase.SetFolder(this, path, newroot)

        kickstart = this.GetRootItem()

        if kickstart and not newroot:
            this.DeleteAllItems()

        if this.GetItemText(kickstart) != path:
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


class DirList(wx.ListCtrl):
    """
    Unlike wxDirCtrl, wxDirList lists not only files + folders, but also their
    last modified and item type, size. You will see it most in your file explorer,
    the main pane.
    This comes with check buttons, which is optional.
    """

    CurrPath: str

    def __init__(this, *args, **kwds):
        kwds["style"] = wx.LC_AUTOARRANGE | wx.LC_EDIT_LABELS | wx.LC_REPORT
        wx.ListCtrl.__init__(this, *args, **kwds)

        this.InsertColumn(0, _("Name"), width=246)
        this.InsertColumn(1, _("Item type"))
        this.InsertColumn(2, _("Last modified"), width=110)
        this.InsertColumn(3, _("Size"))

        this.AssignImageList(imgs, wx.IMAGE_LIST_SMALL)

        this.Bind(wx.EVT_LIST_ITEM_ACTIVATED, this.GoDir)

    def DrawItems(this, path: str = os.path.expanduser("~/")):
        """
        Fill the list control with items;)
        """

        # By default os.path.getsize/os.stat.st_size output will return a value in bytes
        # So this is how we convert it to other units
        # *from SO: a/1094933*
        def sizeof_fmt(num, suffix="B"):
            for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
                if abs(num) < 1024.0:
                    return f"{num:3.1f}{unit}{suffix}"
                num /= 1024.0
            return f"{num:.1f}Yi{suffix}"

        this.DeleteAllItems()

        if not os.path.isdir(path):
            raise NotADirectoryError(path)
        this.CurrPath = path

        for item in os.listdir(path):
            crafted = os.path.join(path, item)
            statinfo = os.stat(crafted)
            it_size = 0

            if os.path.isdir(crafted):
                it_size = ""
                this.InsertItem(0, item, folderidx)
                this.SetItem(0, 1, _("Folder"))
            else:
                it_size = statinfo.st_size
                this.InsertItem(0, item, fileidx)
                this.SetItem(0, 1, _("File"))
            
            m_time = statinfo.st_mtime
            lastmod = time.strftime("%d %b %Y, %H:%M:%S", time.localtime(m_time))

            this.SetItem(0, 2, lastmod)

            if isinstance(it_size, int):
                it_size = sizeof_fmt(it_size)
        
            this.SetItem(0, 3, str(it_size))

    def GoDir(this, evt=None, path: str = ""):
        if evt and not path:
            pos = evt.Index
            name = this.GetItemText(pos)
            item_type = this.GetItemText(pos, 1)

            if item_type == _("Folder"):
                this.DrawItems(os.path.join(this.CurrPath, name))
        else:
            if not path:
                raise Exception(
                    "Who the hell call DirList.GoDir with no directory to go???"
                )
            this.DrawItems(path)

    def GoUp(this, evt):
        this.DrawItems(os.path.dirname(this.CurrPath))
