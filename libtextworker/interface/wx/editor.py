"""
@package libtextworker.interface.wx.editor
@brief Home of the buffed wxStyledTextEditor!
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import wx
import wx.stc

from hashlib import md5
from libtextworker import EDITOR_DIR
from libtextworker.general import CraftItems
from libtextworker.get_config import ConfigurationError, GetConfig

from .miscs import CreateMenu
from .. import stock_editor_configs
from ... import _


class StyledTextControl(wx.stc.StyledTextCtrl):
    """
    A better styled wxStyledTextCtrl.
    Color wxStyledTextCtrl these ways:
    * StyleSetSpace = StyleSetBackground + StyleSetForeground + StyleSetFont ...
    * ColorManager.set*func then ColorManager.configure
    The default style is wx.stc.STC_STYLE_DEFAULT.
    You can make ColorManager do the coloring work for you for mixing the 2 ways above together.
    Else you will want to handle system color changes yourself as well.
    """

    FileLoaded: str = ""
    Hash = md5("".encode("utf-8"))

    def EditorInit(this, config_path: str = ""):
        """
        @since 0.1.3
        Initialize the editor, customized part.
        @param config_path (str): Configuration path (optional - defaults to lib's path)
        """
        if not config_path:
            config_path = CraftItems(EDITOR_DIR, "default.ini")

        this.cfg = GetConfig(stock_editor_configs, config_path)

        # Setup line numbers
        this.LineNumbers()

        # Drag-and-drop support
        this.DNDSupport()

        # Indentation
        this.IndentationSet()

        # Right click menu
        if this.cfg.getkey("menu", "enabled") in this.cfg.yes_values:
            this.Bind(wx.EVT_RIGHT_DOWN, this.MenuPopup)

        # Word wrap
        this.SetWrapMode(this.cfg.getkey("editor", "wordwrap") in this.cfg.yes_values)

        # Editor modifications
        def OnEditorModify(evt):
            this.Hash = md5(this.GetText().encode("utf-8"))
            evt.Skip()
        
        this.Bind(wx.stc.EVT_STC_MODIFIED, OnEditorModify)

    """
    Setup GUI elements.
    """

    def DNDSupport(this) -> bool:
        """Meh DND does not mean do not disturb."""
        if this.cfg.getkey("editor", "dnd_enabled", True, True) \
           not in this.cfg.yes_values:
            return False

        this.SetDropTarget(DragNDropTarget(this))

        return True

    def IndentationSet(this):
        size = int(this.cfg.getkey("indentation", "size", True, True))
        tp = this.cfg.getkey("indentation", "type", True, True)
        show_guide = this.cfg.getkey("indentation", "show_guide", True, True)
        bk_unindent = this.cfg.getkey("indentation", "backspace_unindents", True, True)
        view_ws = this.cfg.getkey("editor", "view_whitespaces", True, True)

        if not 8 >= size > 0:
            raise ConfigurationError("indentation", "size", "Must be in range from 1 to 8")

        if not tp in ["tabs", "spaces"]:
            raise ConfigurationError("indentation", "type", "Must be either 'tabs' or 'spaces'")

        this.SetUseTabs(tp == "tabs")
        this.SetBackSpaceUnIndents(bk_unindent in this.cfg.yes_values)
        this.SetViewWhiteSpace(view_ws in this.cfg.yes_values)
        this.SetIndent(size)
        this.SetIndentationGuides(show_guide in this.cfg.yes_values)

    def LineNumbers(this) -> bool:
        """
        Setup line numbers margin for the editor.
        The margin's default width is 20px.
        """
        state = this.cfg.getkey("editor", "line_count", True, True)

        if state in this.cfg.no_values:
            this.SetMarginWidth(0, 0)
            return False

        this.SetMarginWidth(0, 20)
        this.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        this.SetMarginMask(0, 0)
        this.Bind(wx.stc.EVT_STC_UPDATEUI, this.OnUIUpdate)

        return True

    """
    File-related things
    """

    def LoadFile(this, path: str):
        """
        Loads the content of a file into the editor.
        No check for contents already inside the editor!
        """
        wx.stc.StyledTextCtrl.LoadFile(this, path)
        this.FileLoaded = path
        this.Hash = md5(open(path, "r").read().encode("utf-8"))

    @property
    def IsModified(this):
        """
        Show if the editor has been modified or not.
        Works exactly the same way + implementation as Tkinter's one.
        """
        def checkhash(target): return not this.Hash.digest() == md5(target.encode("utf-8")).digest()
        if not this.FileLoaded: return checkhash("")
        return checkhash(open(this.FileLoaded, "r").read())

    def SetModified(this, state: bool):
        """
        Marks this editor as modified or not.
        wxStyledTextControl seems can't use this.
        """
        raise NotImplementedError

    """
    Events.
    """

    def OnUIUpdate(this, event):  # MS Bing found this - thanks to the people who made it!
        line_count = this.GetLineCount()
        last_line_num = str(line_count)

        if len(last_line_num) <= 4:
            margin_width = 40
        else:
            last_line_width = this.TextWidth(wx.stc.STC_STYLE_LINENUMBER, last_line_num)
            # add some extra space
            margin_width = last_line_width + 4

        # set the margin width
        this.SetMarginWidth(0, margin_width)
        event.Skip()

    def MenuPopup(this, event):
        pt = event.GetPosition()
        menu = CreateMenu(this, [(wx.ID_CUT, None, None, lambda evt: this.Cut(), None),
                                 (wx.ID_COPY, None, None, lambda evt: this.Copy(), None),
                                 (wx.ID_PASTE, None, None, lambda evt: this.Paste(), None),
                                 (None, None, None, None, None),
                                 (wx.ID_UNDO, None, None, lambda evt: this.Undo(), None),
                                 (wx.ID_REDO, None, None, lambda evt: this.Redo(), None),
                                 (wx.ID_DELETE, None, None, lambda evt: this.DeleteBack(), None),
                                 (wx.ID_SELECTALL, None, None, lambda evt: this.SelectAll(), None),
                                 (None, None, None, None, None)])
        readonly = wx.MenuItem(menu, wx.ID_ANY, _("Read only"), _("Set the text to be read-only"), wx.ITEM_CHECK)
        menu.Append(readonly)
        this.Bind(wx.EVT_MENU, lambda evt: (this.SetReadOnly(readonly.IsChecked()),), readonly)

        this.PopupMenu(menu, pt)
        menu.Destroy()


class DragNDropTarget(wx.FileDropTarget, wx.TextDropTarget):
    """
    Drag-and-drop (DND) support for wxStyledTextCtrl.
    """

    def __init__(this, textctrl):
        super().__init__()
        this.Target = textctrl

    def OnDropText(this, x, y, data):
        this.Target.WriteText(data)
        return True

    def OnDragOver(this, x, y, defResult):
        return wx.DragCopy

    def OnDropFiles(this, x, y, filenames):
        this.Target.LoadFile(filenames[0])
        return True
