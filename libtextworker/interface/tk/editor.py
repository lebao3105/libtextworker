#	A cross-platform library for Python apps.
#	Copyright (C) 2023 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

"""
@package libtextworker.interface.tk.editor
@brief Home of Tkinter(Ttk) text editors.
@since 0.1.4: TextWidget is now a StyledTextControl alias (will be removed in the future). Customizations in __init__() are now moved to EditorInit().
"""
from tkinter import BooleanVar, Menu, Text, Misc, TclError
from tkinter.font import Font
from tkinter.ttk import Scrollbar, Frame

try:
    from tklinenums import TkLineNumbers
except:
    LINENUMS = False
else:
    LINENUMS = True

from libtextworker import EDITOR_DIR

from .. import stock_editor_configs
from ...get_config import GetConfig
from .miscs import CreateMenu


class StyledTextControl(Text):
    """
    Customized Tkinter Text widget with some extra features.
    Note: When placing this widget, not only the editor itself, please also place the _frame object as the real editor's parent.
    """

    def __init__(this, master: Misc | None = None, **kwds):
        this._frame = Frame(master)
        Text.__init__(this, this._frame, **kwds)

    def EditorInit(
        this,
        useMenu: bool = False,
        useScrollBars: bool = True,
        custom_config_path: str = EDITOR_DIR + "editor.ini",
        tabwidth: int = 4
    ):
        """
        Initialize the editor, libtextworker's customize part.
        @param useMenu: Enable right-click menu (depends on the user setting - else defaults to disable)
        @param useScrollBars: Show scroll bars
        @param custom_config_path: Custom editor configs path (optional)
        @param custom_theme_path: Custom editor theme path (optional)
        @param tabwidth: Tab (\\t character) width (defaults to user setting else 4)
        """

        this.cfger = GetConfig(stock_editor_configs, custom_config_path)

        this.unRedo = this["undo"]
        this.wrapbtn = BooleanVar(this)

        if this.cfger.getkey("menu", "enabled", False, True, True):
            useMenu = bool(this.cfger.getkey("menu", "enabled"))

        if int(this.cfger.getkey("indentation", "size", True, True, True)):
            tabwidth = int(this.cfger.getkey("indentation", "size"))

        if useMenu:
            this.RMenu = Menu(this, tearoff=0)

            this.addMenucascade = this.RMenu.add_cascade
            this.addMenucheckbtn = this.RMenu.add_checkbutton
            this.addMenucmd = this.RMenu.add_command
            this.addMenuradiobtn = this.RMenu.add_radiobutton
            this.addMenusepr = this.RMenu.add_separator

            this._menu_init()
            this.bind("<Button-3>", this._open_menu)

        if useScrollBars is True:
            this._place_scrollbar()

        # Place the line-numbers margin
        if (
            LINENUMS
            and this.cfger.getkey("editor", "line_count", noraiseexp=True)
            in this.cfger.yes_values
        ):
            ln = TkLineNumbers(this._frame, this, "center")
            ln.pack(fill="y", side="left")
            this.bind(
                "<<Modified>>", lambda evt: this._frame.after_idle(ln.redraw), add=True
            )

    # Place scrollbars
    def _place_scrollbar(this):
        xbar = Scrollbar(this._frame, orient="horizontal", command=this.xview)
        ybar = Scrollbar(this._frame, orient="vertical", command=this.yview)
        # ybar.set = ybar.quit
        xbar.pack(side="bottom", fill="x")
        ybar.pack(side="right", fill="y")

    # Right click menu
    def _menu_init(this):
        this.RMenu = CreateMenu(
            [
                {
                    "label": _("Cut"),
                    "accelerator": "Ctrl+X",
                    "handler": lambda: this.event_generate("<Control-x>"),
                },
                {
                    "label": _("Copy"),
                    "accelerator": "Ctrl+C",
                    "handler": lambda: this.event_generate("<Control-c>")
                },
                {
                    "label": _("Paste"),
                    "accelerator": "Ctrl+V",
                    "handler": lambda: this.event_generate("<Control-v>")
                }
            ]
        )
        if this.unRedo:
            this.RMenu.add_separator()
            this.addMenucmd(
                label=_("Undo"),
                accelerator="Ctrl+Z",
                command=lambda: this.edit_undo(),
            )
            this.addMenucmd(
                label=_("Redo"),
                accelerator="Ctrl+Y",
                command=lambda: this.edit_redo(),
            )

    def _open_menu(this, event):
        try:
            this.RMenu.post(event.x_root, event.y_root)
        finally:
            this.RMenu.grab_release()

    # Wrap mode
    def wrapmode(this, event=None) -> bool:
        """
        Toggle editor word wrap mode.
        Only use with TextWidget.wrapbtn BooleanVar.
        """
        if this.wrapbtn.get() == True:
            this.configure(wrap="none")
            this.wrapbtn.set(False)
            return False
        else:
            this.configure(wrap="word")
            this.wrapbtn.set(True)
            return True

    # Undo/redo forks
    def edit_undo(this) -> None:
        try:
            super().edit_undo()
        except TclError:
            pass

    def edit_redo(this) -> None:
        try:
            super().edit_redo()
        except TclError:
            pass


TextWidget = StyledTextControl
