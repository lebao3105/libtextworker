import io
import wx

class MenuBar(wx.MenuBar):
    def SetParent(self, parent):
        self.parent = parent
        return

    def AddMenu(self, name, items: list):
        """
        Adds a new menu entry.
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
        Don't forget to set the parent of the menubar first! (SetParent function)
        Returns the generated menu.
        """
        target_menu = wx.Menu()

        for id, label, helptext, handler, kind in items:
            if id == None:
                target_menu.AppendSeparator()
            else:
                if kind == None:
                    kind = wx.ITEM_NORMAL
                if label == None:
                    label = ""
                if helptext == None:
                    helptext = ""
                item = target_menu.Append(id, label, helptext, kind)
                self.parent.Bind(wx.EVT_MENU, handler, item)
        self.Append(target_menu, name)
        return target_menu

class XMLBuilder:
    """
    Class to read and build interfaces from a XML file.
    Use this class by call it as a varible, or make a sub-class.
    """
    _Parent = None

    def __init__(self, Parent, FilePath: str, _=None):
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
        xmlload = wx.xml.XmlDocument(io.BytesIO(xrc_data))
        self.Res = wx.xrc.XmlResource()
        self.Res.LoadDocument(xmlload)
    
    def txtLocalize(self, match_obj):
        if self._ == None:
            import gettext
            self._ = gettext.gettext
        return self._(match_obj.group(1))
    
    @property
    def Parent(self):
        return self._Parent
    
    @Parent.setter
    def Parent(self, object):
        self._Parent = object

    def loadObject(self, objectname, objecttype):
        return self.Res.LoadObject(self.Parent, objectname, objecttype)