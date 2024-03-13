"""
@package libtextworker.interface.tk.editor
@brief Home of Tkinter(Ttk) text editors.
"""

# 	A cross-platform library for Python apps.
# 	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
# 	This is a part of the libtextworker project.
# 	Licensed under the GNU General Public License version 3.0 or later.

from hashlib import md5
from tkinter import BooleanVar, Menu, Text, Misc, TclError
from tkinter.font import Font
from tkinter.ttk import Scrollbar, Frame
from typing import overload

from libtextworker.general import test_import
from libtextworker import EDITOR_DIR

from .miscs import CreateMenu
from .. import stock_editor_configs
from ... import _
from ...get_config import GetConfig


class StyledTextControl(Text):
    """
    Customized Tkinter Text widget with some extra features.
    Note: Use StyledTextControl._frame as the real StyledTextControl's parent.
    """

    FileLoaded: str = ""
    Hash = md5("".encode("utf-8"))

    def __init__(this, master: Misc | None = None, **kwds):
        this._frame = Frame(master)
        Text.__init__(this, this._frame, **kwds)

    def EditorInit(this, useMenu: bool = False, useScrollBars: bool = True,
                   custom_config_path: str = EDITOR_DIR + "/editor.ini",
                   tabwidth: int = 4):
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
        if test_import("tklinenums") and this.cfger.getkey("editor", "line_count", noraiseexp=True) in this.cfger.yes_values:
            from tklinenums import TkLineNumbers
            ln = TkLineNumbers(this._frame, this, "center")
            ln.pack(fill="y", side="left")
            this.bind("<<Modified>>", lambda evt: this._frame.after_idle(ln.redraw), add=True)

        # On editor modify
        def OnEditorModify(evt):
            this.Hash = md5(this.get(1.0, "end").encode("utf-8"))
        this.bind("<<Modified>>", OnEditorModify, add=True)

        # Tab size
        this.config(tabs=Font(font=this['font']).measure('  '*tabwidth))

    # Place scrollbars
    def _place_scrollbar(this):
        xbar = Scrollbar(this._frame, orient="horizontal", command=this.xview)
        ybar = Scrollbar(this._frame, orient="vertical", command=this.yview)

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
                    "handler": lambda: this.event_generate("<Control-c>"),
                },
                {
                    "label": _("Paste"),
                    "accelerator": "Ctrl+V",
                    "handler": lambda: this.event_generate("<Control-v>"),
                },
            ]
        )

        if this.unRedo:
            this.RMenu.add_separator()
            
            this.addMenucmd(label=_("Undo"), accelerator="Ctrl+Z",
                            command=lambda: this.edit_undo())
            
            this.addMenucmd(label=_("Redo"), accelerator="Ctrl+Y",
                            command=lambda: this.edit_redo())

    def _open_menu(this, event):
        try:
            this.RMenu.post(event.x_root, event.y_root)
        finally:
            this.RMenu.grab_release()

    # File load / save
    @property
    def IsModified(this) -> bool:
        """
        Probably this will let you know if the editor content has been cooked or not.
        """
        def checkhash(target): return not this.Hash.digest() == md5(target.encode("utf-8")).digest()
        if not this.FileLoaded: return checkhash("") # Currently can't use .get?
        return checkhash(open(this.FileLoaded, "r").read())

    def LoadFile(this, path: str):
        """
        Load a file.
        Warning: the path must exists on the file system, else
         an exception will be raised (no handle from us).
        Also this will OVERWRITE existing editor CONTENT, so make
         sure you have your backup way.
        """
        content = open(path, "r").read()
        this.insert(1.0, content)
        this.FileLoaded = path
        this.Hash = md5(content.encode("utf-8"))
    
    @overload
    def SaveFile(this, path: str):
        """
        Write the current editor contents into a file.
        """
        content = this.get(1.0, "end")
        open(path, "w").write(content)
        this.Hash = md5(content.encode("utf-8"))
    
    @overload
    def SaveFile(this):
        """
        Write the current editor contents into the loaded file, if any.
        If not able to, do nothing.
        """
        if this.FileLoaded: return this.SaveFile(this.FileLoaded)

    # Wrap mode
    def wrapmode(this, event=None) -> bool:
        """
        Toggle editor word wrap mode.
        Only use with TextWidget.wrapbtn BooleanVar.
        """
        value = this.wrapbtn.get()
        this.configure(wrap="none" if value else "word")
        this.wrapbtn.set(not value)
        return not value

    def edit_undo(this) -> None:
        """
        Undoes the last edit option, if able to.
        """
        try:
            super().edit_undo()
        except TclError:
            pass

    def edit_redo(this) -> None:
        """
        Redoes the last undone edit option, if able to.
        """
        try:
            super().edit_redo()
        except TclError:
            pass


TextWidget = StyledTextControl
