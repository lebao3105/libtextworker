import re
import wx
import wx.xrc


def CreateMenu(parent, items: list) -> wx.Menu:
    """
    Create a new wx.Menu with a list of commands.
    Menu items use the following format:
    ```
    [   # Must be a list
        (id, label, helptext, handler, None),
        ...
        (id, label, helptext, handler, wx.ITEM_CHECK), # Add check item
        (id, label, helptext, handler, wx.ITEM_RADIO) # Add radio item
        (None, None, None, None, None) # Add separator
    ]
    ```
    Sub-menus are not supported.
    Returns the generated menu.
    """
    target_menu = wx.Menu()

    for id, label, helptext, handler, kind in items:
        if id == label == helptext == handler == kind == None:
            target_menu.AppendSeparator()
        else:
            if id == None:
                id = wx.ID_ANY
            if kind == None:
                kind = wx.ITEM_NORMAL
            if label == None:
                label = ""
            if helptext == None:
                helptext = ""
            item = target_menu.Append(id, label, helptext, kind)
            parent.Bind(wx.EVT_MENU, handler, item)
    return target_menu


class XMLBuilder:
    """
    Class to read and build interfaces from a XML file.
    Use this class by call it as a varible, or make a sub-class.
    """

    def __init__(self, Parent, FilePath: str, _=None):
        """
        Constructor of the class.
        @param Parent: wxPython window
        @param FilePath: XRC file to load
        @param _: (initialized) gettext
        """
        self.Parent = Parent
        self._ = _

        # Setup translation
        # Cre: https://wiki.wxpython.org/XRCAndI18N
        ## Initial load
        with open(FilePath, encoding="utf-8") as f:
            xrc_data = f.read()

        ## Replace texts with translated ones
        xrc_data = re.sub("_\(['\"](.*?)['\"]\)", self.txtLocalize, xrc_data)
        xrc_data = xrc_data.encode("utf8")

        # Call out the resource file, with translated strings
        self.Res = wx.xrc.XmlResource()
        self.Res.LoadFromBuffer(xrc_data)

    def txtLocalize(self, match_obj):
        if self._ == None:
            import gettext

            self._ = gettext.gettext
        return self._(match_obj.group(1))

    def loadObject(self, objectname, objecttype):
        return self.Res.LoadObject(self.Parent, objectname, objecttype)
