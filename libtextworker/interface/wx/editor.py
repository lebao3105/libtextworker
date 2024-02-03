"""
@package libtextworker.interface.wx.editor
"""
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

    def EditorInit(self, config_path: str = ""):
        """
        @since 0.1.3
        Initialize the editor, customized part.
        @param config_path (str): Configuration path (optional - defaults to lib's path)
        """
        if not config_path:
            config_path = CraftItems(EDITOR_DIR, "default.ini")

        self.cfg = GetConfig(stock_editor_configs, config_path)

        # Setup line numbers
        self.LineNumbers()

        # Drag-and-drop support
        self.DNDSupport()

        # Indentation
        self.IndentationSet()

        # Right click menu
        if self.cfg.getkey("menu", "enabled") in self.cfg.yes_values:
            self.Bind(wx.EVT_RIGHT_DOWN, self.MenuPopup)

        # Word wrap
        self.SetWrapMode(self.cfg.getkey("editor", "wordwrap") in self.cfg.yes_values)

        # Editor modifications
        def OnEditorModify(evt):
            self.Hash = md5(self.GetText().encode("utf-8"))
            evt.Skip()
        
        self.Bind(wx.stc.EVT_STC_MODIFIED, OnEditorModify)

    """
    Setup GUI elements.
    """

    def DNDSupport(self) -> bool:
        """Meh DND does not mean do not disturb."""
        if self.cfg.getkey("editor", "dnd_enabled", True, True) \
           not in self.cfg.yes_values:
            return False

        dt = DragNDropTarget(self)
        self.SetDropTarget(dt)

        return True

    def IndentationSet(self):
        size = int(self.cfg.getkey("indentation", "size", True, True))
        tp = self.cfg.getkey("indentation", "type", True, True)
        show_guide = self.cfg.getkey("indentation", "show_guide", True, True)
        bk_unindent = self.cfg.getkey("indentation", "backspace_unindents", True, True)
        view_ws = self.cfg.getkey("editor", "view_whitespaces", True, True)

        if not 8 >= size > 0:
            raise ConfigurationError(
                "indentation", "size", "Must be in range from 1 to 8"
            )

        if not tp in ["tabs", "spaces"]:
            raise ConfigurationError(
                "indentation", "type", "Must be either 'tabs' or 'spaces'"
            )

        self.SetUseTabs(tp == "tabs")
        self.SetBackSpaceUnIndents(bk_unindent in self.cfg.yes_values)
        self.SetViewWhiteSpace(view_ws in self.cfg.yes_values)
        self.SetIndent(size)
        self.SetIndentationGuides(show_guide in self.cfg.yes_values)

    def LineNumbers(self) -> bool:
        """
        Setup line numbers margin for the editor.
        The margin's default width is 20px.
        """
        state = self.cfg.getkey("editor", "line_count", True, True)

        if state in self.cfg.no_values:
            self.SetMarginWidth(0, 0)
            return False

        self.SetMarginWidth(0, 20)
        self.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginMask(0, 0)
        self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUIUpdate)

        return True

    """
    File-related things
    """

    def LoadFile(self, path: str):
        """
        Loads the content of a file into the editor.
        No check for contents already inside the editor!
        """
        wx.stc.StyledTextCtrl.LoadFile(self, path)
        self.FileLoaded = path

    @property
    def IsModified(self):
        """
        Show if the editor has been modified or not.
        Works exactly the same way + implementation as Tkinter's one.
        """
        def checkhash(target): return not self.Hash.digest() == md5(target.encode("utf-8")).digest()
        if not self.FileLoaded: return checkhash("")
        return checkhash(open(self.FileLoaded, "r").read())

    def SetModified(self, state: bool):
        """
        Marks this editor as modified or not.
        wxStyledTextControl seems can't use this.
        """
        raise NotImplementedError

    """
    Events.
    """

    def OnUIUpdate(
        self, event
    ):  # MS Bing found this - thanks to the people who made it!
        line_count = self.GetLineCount()
        last_line_num = str(line_count)

        if len(last_line_num) <= 4:
            margin_width = 40
        else:
            last_line_width = self.TextWidth(wx.stc.STC_STYLE_LINENUMBER, last_line_num)
            # add some extra space
            margin_width = last_line_width + 4

        # set the margin width
        self.SetMarginWidth(0, margin_width)
        event.Skip()

    def MenuPopup(self, event):
        pt = event.GetPosition()
        menu = CreateMenu(
            self,
            [
                (wx.ID_CUT, None, None, lambda evt: self.Cut(), None),
                (wx.ID_COPY, None, None, lambda evt: self.Copy(), None),
                (wx.ID_PASTE, None, None, lambda evt: self.Paste(), None),
                (None, None, None, None, None),
                (wx.ID_UNDO, None, None, lambda evt: self.Undo(), None),
                (wx.ID_REDO, None, None, lambda evt: self.Redo(), None),
                (wx.ID_DELETE, None, None, lambda evt: self.DeleteBack(), None),
                (wx.ID_SELECTALL, None, None, lambda evt: self.SelectAll(), None),
                (None, None, None, None, None),
            ],
        )
        readonly = wx.MenuItem(
            menu,
            wx.ID_ANY,
            _("Read only"),
            _("Set the text to be read-only"),
            wx.ITEM_CHECK,
        )
        menu.Append(readonly)
        self.Bind(
            wx.EVT_MENU,
            lambda evt: (self.SetReadOnly(readonly.IsChecked()),),
            readonly,
        )

        self.PopupMenu(menu, pt)
        menu.Destroy()


class DragNDropTarget(wx.FileDropTarget, wx.TextDropTarget):
    """
    Drag-and-drop (DND) support for wxStyledTextCtrl.
    """

    def __init__(self, textctrl):
        super().__init__()
        self.Target = textctrl

    def OnDropText(self, x, y, data):
        self.Target.WriteText(data)
        return True

    def OnDragOver(self, x, y, defResult):
        return wx.DragCopy

    def OnDropFiles(self, x, y, filenames):
        if len(filenames) > 0:
            self.Target.LoadFile(filenames)
        return True
