"""
@package libtextworker.interface.wx.miscs
@brief Misc stuffs for wxPython.
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import os
import re
import wx
import wx.aui
import wx.xrc

from types import ModuleType
from typing import Callable
from warnings import warn


def CreateMenu(parent, items: list[tuple]) -> wx.Menu:
    """
    Create a new wx.Menu with a list of commands.
    Menu items use the following format:
    ```
    (id, label, helptext, handler, kind) # Stay in a tuple like this
    ```
    * id: Menu item id (wx.ID_* - ID_ANY is the default)
    * label: Menu item label
    * helptext: Text to be shown in the status bar (on the left)
    * handler (Callable): Callback
    * kind: Type of the menu item (wx.ITEM_*) (wx.ITEM_NORMAL by default)

    If you want to append a separator, make all items in the tuple None.
    Sub-menus are not supported.
    Returns the generated menu.
    """
    target_menu = wx.Menu()
    for id, label, helptext, handler, kind in items:
        if id == label == helptext == handler == kind == None:
            target_menu.AppendSeparator()
        else:
            if not id: id = wx.ID_ANY
            if not kind: kind = wx.ITEM_NORMAL
            if not label: label = ""
            if not helptext: helptext = ""
            item = target_menu.Append(id, label, helptext, kind)
            parent.Bind(wx.EVT_MENU, handler, item)
    return target_menu


def BindMenuEvents(obj: wx.Window, menu: wx.Menu, items: list[tuple[Callable, int]]):
    """
    Bind wxEVT_MENU events an easier way. Ideal for XRC menus.
    @param obj (wx.Window): Object to call Bind() from
    @param menu (wx.Menu): Target menu
    @param items (list of tuples of [Callable, int]): List of tuples, each tuple has a function + menu item index.
    """
    for callback, pos in items:
        obj.Bind(wx.EVT_MENU, callback, menu.FindItemByPosition(pos))


def BindEvents(obj: wx.Window, items: list[tuple[wx.PyEventBinder, Callable, int]]):
    """
    Bind events for a wxWindow.
    @param obj (wx.Window): Object to call Bind() from
    @param items (list of tuples of [Callable, int]): Events

    Expaining "items" parameter:
    * wx.PyEventBinder object: wx event (wx.EVT_*)
    * Callable object: callback
    * int object: position of the widget we will bind the event to. Find it by obj.GetChildren()[int].
    """

    for evt_type, callback, pos in items:
        obj.Bind(evt_type, callback, obj.GetChildren()[pos])


class XMLBuilder:
    """
    Class to read and build interfaces from a XML file.
    Use this class by call it as a varible, or make a sub-class.
    """

    def __init__(self, Parent: wx.Window | None, FilePath: str, _: Callable[[str], str] | None = None):
        """
        Constructor of the class.
        @param Parent: wx.Window object
        @param FilePath: XRC file to load
        @param _: gettext.gettext or whatever you want, for translations
        """

        """
        @since 0.1.3:
            Changed self.Parent -> self.Master to avoid confusion when the class
            is being subclassed with other wxPython classes
        """
        self.Master: wx.Window | None = Parent
        self._ = _

        # Setup translation
        # Cre: https://wiki.wxpython.org/XRCAndI18N
        ## Initial load
        with open(FilePath, encoding="utf-8") as f:
            xrc_data = f.read()

        ## Replace texts with translated ones
        xrc_data = re.sub("_(['\"](.*?)['\"])", self.txtLocalize, xrc_data) \
                     .encode("utf8")

        # Call out the resource file, with translated strings
        self.Res = wx.xrc.XmlResource()
        self.Res.LoadFromBuffer(xrc_data)

    def txtLocalize(self, match_obj: re.Match[str]):
        if self._ == None:
            import gettext

            self._ = gettext.gettext
        return self._(match_obj.group(1))

    def loadObject(self, objectname, objecttype):
        """
        Load an XRC object.
        Mainly used for calling the top-level panel (e.g Frame, Dialog).
        You may see "Object not found" message, especially when XRC does not store
        element name.
        Tip: to prevent this, use children-communicate functions such as
            GetSizer, GetChilren, or even wx.FindWindowBy*.
        """
        return self.Res.LoadObject(self.Master, objectname, objecttype)
    
def localizePy(path: str, importText: str | None = None, ignoreDoneWork: bool = True) -> ModuleType:
    """
    Localizes generated Python code, if no wxGetTranslation or gettext used there.
    
    wxFormBuilder uses gettext for generated files since version 4.2.1.

    @param path : The path to the Python code
    @param importText : The from .. import statement that will be added to the file (like importing gettext)
    @param ignoreDoneWork: Ignore localized file
    @returns result (ModuleType): Imported @path
    """

    def importmodule():
        name = os.path.basename(path)

        import importlib.util
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec != None
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    assert os.path.exists(path) and os.path.isfile(path), f"{path} is neither a file nor an existing item on the file system"
    content = open(path, "r").read()

    if not ignoreDoneWork:
        assert content.startswith(path) == False, \
            "Already localized. To avoid the file being broken, this cannot continue.\n" \
            "Replace the file with newly generated code from your preferred GUI builder and try again."
    else:
        if content.startswith(importText): # Already localized?
            warn(f"{path} seems to be localized. This function checks if the first line was {importText},"
                 f" so the final result maybe incorrect. If so, remove that {importText} and try again.")
            return importmodule()
    
    if not importText.endswith("\n"): importText += "\n"
    func = importText.split(" ")[-1] # Get the translate function (e.g gettext in from gettext import gettext)
    content = importText + content # Add import statement

    # Made with the help of, yeah, AI. (cuz I'm bad at regex)
    # I have modified it myself for the most perfect pattern.
    # All strings in wxFormBuilder generated Python code are unicode type:
    # u"<content>"
    # The final regex group looks for space (just one space) OR a comma (,) but NOT include it to the catch result.
    # One drawback is that numberic only strings are included, but can be skipped below.
    pattern = r'u(")(.+?)(")(?=[\s,])'
    matches: list[tuple[str, str, str]] = re.findall(pattern, content)
    
    for match in matches:
        # The match result will be a list of 
        # (quote, string, matching quote) tuples.
        # Skip numberic/float strings.
        if match[1].isdigit() or match[1].isdecimal():
            continue
        else:
            localized = f'{func}(u"{match[1]}")'
            content = content.replace(f'u"{match[1]}"', localized)
    
    open(path, "w").write(content)

    return importmodule()

