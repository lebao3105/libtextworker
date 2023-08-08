"""
@package libtextworker.interface.tk.editor
@brief Home of Tkinter(Ttk) text editors.
@since 0.1.4: TextWidget is now a StyledTextControl alias (will be removed in the future). Customizations in __init__() are now moved to EditorInit().
"""
from tkinter import BooleanVar, Menu, Text, Misc, TclError
from tkinter.ttk import Scrollbar, Frame

try:
    from tklinenums import TkLineNumbers
except:
    LINENUMS = False
else:
    LINENUMS = True

from libtextworker import EDITOR_DIR, THEMES_DIR

from . import ColorManager
from .. import stock_editor_configs
from ...get_config import GetConfig
from .miscs import CreateMenu


class StyledTextControl(Text):
    """
    Customized Tkinter Text widget with some extra features.
    Note: When placing this widget, not only the editor itself, please also place the _frame object as the real editor's parent.
    """

    def __init__(self, master: Misc | None = None, **kwds):
        self._frame = Frame(master)
        super().__init__(self._frame, **kwds)

    def EditorInit(
        self,
        useMenu: bool = False,
        useScrollBars: bool = True,
        custom_config_path: str = EDITOR_DIR + "editor.ini",
        custom_theme_path: str = THEMES_DIR + "default.ini",
        tabwidth: int = 4,
    ):
        """
        Initialize the editor, libtextworker's customize part.
        @param useMenu: Enable right-click menu (depends on the user setting - else defaults to disable)
        @param useScrollBars: Show scroll bars
        @param custom_config_path: Custom editor configs path (optional)
        @param custom_theme_path: Custom editor theme path (optional)
        @param tabwidth: Tab (\\t character) width (defaults to user setting else 4)
        """

        self.cfger = GetConfig(stock_editor_configs, custom_config_path)
        self.clrmgr = ColorManager(customfilepath=custom_theme_path)

        self.unRedo = self["undo"]
        self.wrapbtn = BooleanVar(self)

        if self.cfger.getkey("menu", "enabled", False, True, True):
            useMenu = bool(self.cfger.getkey("menu", "enabled"))

        if int(self.cfger.getkey("indentation", "size", False, True, True)):
            tabwidth = int(self.cfger.getkey("indentation", "size"))

        if useMenu:
            self.RMenu = Menu(self, tearoff=0)

            self.addMenucascade = self.RMenu.add_cascade
            self.addMenucheckbtn = self.RMenu.add_checkbutton
            self.addMenucmd = self.RMenu.add_command
            self.addMenuradiobtn = self.RMenu.add_radiobutton
            self.addMenusepr = self.RMenu.add_separator

            self._menu_init()
            self.bind("<Button-3>", self._open_menu)

        if useScrollBars is True:
            self._place_scrollbar()

        # Place the line-numbers margin
        if (
            LINENUMS
            and self.cfger.getkey("editor", "line_count", noraiseexp=True)
            in self.cfger.yes_values
        ):
            ln = TkLineNumbers(self._frame, self, "center")
            ln.pack(fill="y", side="left")
            self.bind(
                "<<Modified>>", lambda evt: self._frame.after_idle(ln.redraw), add=True
            )

        self.clrmgr.configure(self._frame, False)
        self.configure(tabs=self.clrmgr.GetFont.measure(" " * tabwidth))

    # Place scrollbars
    def _place_scrollbar(self):
        xbar = Scrollbar(self._frame, orient="horizontal", command=self.xview)
        ybar = Scrollbar(self._frame, orient="vertical", command=self.yview)
        # ybar.set = ybar.quit
        xbar.pack(side="bottom", fill="x")
        ybar.pack(side="right", fill="y")

    # Right click menu
    def _menu_init(self):
        self.RMenu = CreateMenu(
            [
                {
                    "label": _("Cut"),
                    "accelerator": "Ctrl+X",
                    "handler": lambda: self.event_generate("<Control-x>"),
                }
            ]
        )
        # self.addMenucmd(
        #     label=_("Cut"),
        #     accelerator="Ctrl+X",
        #     command=lambda: self.event_generate("<Control-x>"),
        # )
        # self.addMenucmd(
        #     label=_("Copy"),
        #     accelerator="Ctrl+C",
        #     command=lambda: self.event_generate("<Control-c>"),
        # )
        # self.addMenucmd(
        #     label=_("Paste"),
        #     accelerator="Ctrl+V",
        #     command=lambda: self.event_generate("<Control-v>"),
        # )
        # if self.unRedo:
        #     self.RMenu.add_separator()
        #     self.addMenucmd(
        #         label=_("Undo"),
        #         accelerator="Ctrl+Z",
        #         command=lambda: self.edit_undo(),
        #     )
        #     self.addMenucmd(
        #         label=_("Redo"),
        #         accelerator="Ctrl+Y",
        #         command=lambda: self.edit_redo(),
        #     )

    def _open_menu(self, event):
        try:
            self.RMenu.post(event.x_root, event.y_root)
        finally:
            self.RMenu.grab_release()

    # Wrap mode
    def wrapmode(self, event=None) -> bool:
        """
        Toggle editor word wrap mode.
        Only use with TextWidget.wrapbtn BooleanVar.
        """
        if self.wrapbtn.get() == True:
            self.configure(wrap="none")
            self.wrapbtn.set(False)
            return False
        else:
            self.configure(wrap="word")
            self.wrapbtn.set(True)
            return True

    # Undo/redo forks
    def edit_undo(self) -> None:
        try:
            super().edit_undo()
        except TclError:
            pass

    def edit_redo(self) -> None:
        try:
            super().edit_redo()
        except TclError:
            pass


TextWidget = StyledTextControl
