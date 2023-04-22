import wx
import wx.stc

from libtextworker import EDITOR_DIR
from libtextworker.get_config import ConfigurationError, GetConfig

from libtextworker.interface.wx import clrmgr
from libtextworker.interface.wx.miscs import CreateMenu

default_configs = {
    "indentation": {"size": 4, "type": "tabs", "show_guide": "yes"},
    "menu": {"enabled": "yes"},
    "editor": {"line_count": "yes", "dnd_enabled": "yes"},
}


class StyledTextControl(wx.stc.StyledTextCtrl):
    def __init__(self, *args, **kw):
        kw["style"] = kw.get("style", 0) | wx.stc.STC_STYLE_DEFAULT
        super().__init__(*args, **kw)

        self.clrmgr = clrmgr
        self.cfg = GetConfig(default_configs, EDITOR_DIR + "editor.ini")

        # Base editor color
        self.SetupEditorColor()

        # Setup line numbers
        self.LineNumbers()

        # Drag-and-drop support
        self.DNDSupport()

        # Indentation
        self.IndentationSet()

        # Right click menu
        if self.cfg.getkey("menu", "enabled") in [True, "yes"]:
            self.Bind(wx.EVT_RIGHT_DOWN, self.MenuPopup)

    def DNDSupport(self) -> bool:
        if (
            self.cfg.getkey("editor", "dnd_enabled", True, True, getbool=True) != True
            or "yes"
        ):
            return False

        dt = DragNDropTarget(self)
        self.SetDropTarget(dt)

        return True

    def IndentationSet(self) -> bool:
        size = int(self.cfg.getkey("indentation", "size", True, True, getbool=False))
        tp = self.cfg.getkey("indentation", "type", True, True)
        show_guide = self.cfg.getkey(
            "indentation", "show_guide", True, True, getbool=True
        )

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
        if self.cfg.getkey("editor", "line_count", True, True, getbool=True) not in [
            True,
            "yes",
        ]:
            self.SetMarginWidth(1, 0)
            return False

        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginMask(1, 0)
        self.SetMarginWidth(1, 40)

        return True

    def SetupEditorColor(self):
        bg, fg = self.clrmgr._get_color()
        self.StyleSetSpec(0, "fore:{},back:{}".format(fg, bg))
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, "fore:{},back:{}".format(fg, bg))

        self.clrmgr.setcolorfunc(
            "textw", self.StyleSetBackground, wx.stc.STC_STYLE_DEFAULT
        )
        self.clrmgr.setfontcfunc(
            "textw", self.StyleSetForeground, wx.stc.STC_STYLE_DEFAULT
        )
        self.clrmgr.configure(self)

        self.Bind(wx.stc.EVT_STC_MODIFIED, self.OnSTCModify)

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

    def MenuPopup(self, evt):
        pt = evt.GetPosition()
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
            lambda evt: (
                self.SetReadOnly(readonly.IsChecked()),
                print("set to {}".format(readonly.IsChecked())),
            ),
            readonly,
        )

        self.PopupMenu(menu, pt)
        menu.Destroy()


class DragNDropTarget(wx.FileDropTarget, wx.TextDropTarget):
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
