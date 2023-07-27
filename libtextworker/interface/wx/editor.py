import wx
import wx.stc

from libtextworker import EDITOR_DIR
from libtextworker.get_config import ConfigurationError, GetConfig

from . import ColorManager
from .miscs import CreateMenu
from .. import stock_editor_configs


class StyledTextControl(wx.stc.StyledTextCtrl):
    """
    A better styled wxStyledTextCtrl.
    @since version 0.1.3:
        Moved all customs from __init__ (derived) to EditorInit func()
        Auto-expand linenumber margin
    """

    def EditorInit(self, config_path: str = "", color_config_path: str = ""):
        """
        @since 0.1.3
        Initialize the editor, customized part.
        You can't ignore __init__() function;)
        @param config_path (str): Configuration path (optional - defaults to lib's path)
        @param color_config_path (str): Configuration path for the color (optional)
        """
        if not config_path:
            config_path = EDITOR_DIR + "default.ini"

        self.clrmgr = ColorManager(customfilepath=color_config_path)
        self.cfg = GetConfig(stock_editor_configs, config_path)

        # Base editor color
        self.SetupEditorColor()

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
        self.SetWrapMode(bool(self.cfg.getkey("editor", "wordwrap")))

        # Multiple-selection support.
        # Since we can't make "Change all occurrences" features like VSCode
        # which makes this feature really work, I disabled it now.

        # self.SetMultipleSelection(True)
        # self.SetAdditionalCaretsVisible(True)
        # self.Bind(wx.EVT_LEFT_UP, self.MultiSelection)

    """
    Setup GUI elements.
    """

    def DNDSupport(self) -> bool:
        if (
            self.cfg.getkey("editor", "dnd_enabled", True, True)
            not in self.cfg.yes_values
        ):
            return False

        dt = DragNDropTarget(self)
        self.SetDropTarget(dt)

        return True

    def IndentationSet(self) -> bool:
        size = int(self.cfg.getkey("indentation", "size", True, True))
        tp = self.cfg.getkey("indentation", "type", True, True)
        show_guide = self.cfg.getkey("indentation", "show_guide", True, True)

        if not 8 >= size > 0:
            raise ConfigurationError(
                "indentation", "size", "Must be in range from 1 to 8"
            )

        if not tp in ["tabs", "spaces"]:
            raise ConfigurationError(
                "indentation", "type", "Must be either 'tabs' or 'spaces'"
            )

        self.SetIndent(size)

        if show_guide == True or "yes":
            self.SetIndentationGuides(True)
        else:
            self.SetIndentationGuides(False)

    def LineNumbers(self) -> bool:
        state = self.cfg.getkey("editor", "line_count", True, True)
        if state in self.cfg.no_values:
            self.SetMarginWidth(0, 0)
            return False

        self.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginMask(0, 0)

        return True

    def SetupEditorColor(self):
        bg, fg = self.clrmgr.GetColor()
        # print(bg, fg)
        self.StyleClearAll()
        self.StyleSetSpec(0, "fore:{},back:{}".format(fg, bg))
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, "fore:{},back:{}".format(fg, bg))

        self.clrmgr.setcolorfunc(
            "textw",
            self.StyleSetBackground,
            {"style": wx.stc.STC_STYLE_DEFAULT, "back": "%(color-rgb)"},
        )
        self.clrmgr.setfontcfunc(
            "textw",
            self.StyleSetForeground,
            {"style": wx.stc.STC_STYLE_DEFAULT, "fore": "%(font-rgb)"},
        )
        self.clrmgr.configure(self, False)

        self.Bind(wx.stc.EVT_STC_MODIFIED, self.OnSTCModify)
        self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUIUpdate)

    """
    Events.
    """

    def OnSTCModify(self, event):
        if event:
            pos = event.GetPosition()
            length = event.GetLength()
        else:
            pos = 0
            length = self.GetLength()
        self.StartStyling(pos)
        self.SetStyling(length, 0)
        event.Skip()

    def OnUIUpdate(self, event):  # MS Bing helped me this
        """
        @since Version 0.1.3
        Auto-expand linenumber margin.
        """
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

    # def MultiSelection(self, event: wx.MouseEvent):
    #     kbs = wx.KeyboardState()
    #     if event.ControlDown() and kbs.ControlDown():
    #         currpos = self.GetCurrentPos()
    #         wordstartpos = self.WordStartPosition(currpos, True)
    #         wordendpos = self.WordEndPosition(wordstartpos, True)
    #         self.AddSelection(wordstartpos, currpos)
    #         self.AddSelection(currpos, wordendpos)
    #     event.Skip()


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
