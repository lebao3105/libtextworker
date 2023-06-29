"""
@package libtextworker.interface.tk.editor
@brief Home of Tkinter(Ttk) text editors.
@since 0.1.4: TextWidget is now a StyledTextControl alias (will be removed in the future). Customizations in __init__() are now moved to EditorInit().
"""
from tkinter import BooleanVar, Menu, Text, ttk
from typing import Literal

from libtextworker import EDITOR_DIR

from . import ColorManager
from ..import stock_editor_configs
from ...get_config import GetConfig


class StyledTextControl(Text):
    """
    Customized Tkinter Text widget with some extra features.

    You can set the wrapbtn variable to your own wrapbtn to use the wrap feature.
    The wrap function is wrapmode(event=None).
    """

    clrmgr = ColorManager()
    cfger = GetConfig(stock_editor_configs, EDITOR_DIR + "editor.ini")

    def EditorInit(
        self,
        useMenu: bool = cfger.getkey("menu", "enabled", True, True, True) in cfger.yes_values,
        useScrollBars: bool = True,
        unRedoable: bool = True,
        textwrap: Literal["char", "none", "word"] = "word"
    ):
        """
        Initialize the editor, libtextworker's customize part.
        @param useMenu: Enable right-click menu (depends on the user setting - else defaults to disable)
        @type useMenu: boolean
        @param useScrollBars: Show scroll bars
        @type useScrollBars: boolean
        @param unRedoable: Set the text widget to be able to use undo/redo (default is True)
        @type unRedoable: boolean
        @param textwrap: Text wrap option ("char(acter)", "none" (turn off) or "word")
        @type textwrap: str (limited to 3 options above)
        """

        self.unRedo = unRedoable
        self.wrapbtn = BooleanVar(self)

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
        
        self.clrmgr.configure(self, True)
        self.configure(wrap=textwrap, undo=unRedoable)

    # Place scrollbars
    def _place_scrollbar(self):
        xbar = ttk.Scrollbar(self, orient="horizontal", command=self.xview)
        ybar = ttk.Scrollbar(self, orient="vertical", command=self.yview)
        ybar.set = (ybar.quit)
        xbar.pack(side="bottom", fill="x")
        ybar.pack(side="right", fill="y")

    # Right click menu
    def _menu_init(self):
        self.addMenucmd(
            label=_("Cut"),
            accelerator="Ctrl+X",
            command=lambda: self.event_generate("<Control-x>"),
        )
        self.addMenucmd(
            label=_("Copy"),
            accelerator="Ctrl+C",
            command=lambda: self.event_generate("<Control-c>"),
        )
        self.addMenucmd(
            label=_("Paste"),
            accelerator="Ctrl+V",
            command=lambda: self.event_generate("<Control-v>"),
        )
        if self.unRedo:
            self.RMenu.add_separator()
            self.addMenucmd(
                label=_("Undo"),
                accelerator="Ctrl+Z",
                command=lambda: self.edit_undo(),
            )
            self.addMenucmd(
                label=_("Redo"),
                accelerator="Ctrl+Y",
                command=lambda: self.edit_redo(),
            )

    def _open_menu(self, event):
        try:
            self.RMenu.post(event.x_root, event.y_root)
        finally:
            self.RMenu.grab_release()

    # Wrap mode
    def wrapmode(self, event=None) -> bool:
        """
        Toggle editor wrap mode.
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

TextWidget = StyledTextControl