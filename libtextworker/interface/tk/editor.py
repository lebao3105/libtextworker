import tkinter.ttk as ttk
from tkinter import BooleanVar, Menu, Text


class TextWidget(Text):
    def __init__(
        self,
        parent,
        useMenu: bool = True,
        useScrollbars: bool = True,
        unRedo: bool = True,
        **kwds,
    ):
        """
        Customized Tkinter Text widget with a basic right-click menu.
        @param parent : Where to place this widget
        @param useMenu (bool) : Enable right-click menu or not
        @param unredo (bool)=True : Undo Redo
        @param useScrollbars (bool)=True : Use scrollbars
        @param **kwds : Other configurations (tkinter.Text)

        You can set TextWidget.wrapbtn to your own wrapbtn to use the wrap feature.
        The wrap function is wrapmode(event=None).
        """
        self.unRedo = kwds["undo"] = kwds.get("undo", 0) or unRedo
        super().__init__(parent, **kwds)

        self.wrapbtn = BooleanVar(self)
        self.wrapbtn.set(True)

        if useMenu != None:
            self.enableMenu = useMenu

        if self.enableMenu is True:
            self.RMenu = Menu(self, tearoff=0)
            self._menu_init()
            self.bind("<Button-3>", lambda event: self._open_menu(event))

        if useScrollbars is True:
            self._place_scrollbar()

        self.configure(wrap="word")
        self.configure(undo=unRedo)

    # Place scrollbars
    def _place_scrollbar(self):
        xbar = ttk.Scrollbar(self, orient="horizontal", command=self.xview)
        ybar = ttk.Scrollbar(self, orient="vertical", command=self.yview)
        xbar.pack(side="bottom", fill="x")
        ybar.pack(side="right", fill="y")

    # Right click menu
    def _menu_init(self):
        addcmd = self.RMenu.add_command
        root = self.master
        addcmd(
            label=_("Cut"),
            accelerator="Ctrl+X",
            command=lambda: root.event_generate("<Control-x>"),
        )
        addcmd(
            label=_("Copy"),
            accelerator="Ctrl+C",
            command=lambda: root.event_generate("<Control-c>"),
        )
        addcmd(
            label=_("Paste"),
            accelerator="Ctrl+V",
            command=lambda: root.event_generate("<Control-v>"),
        )
        if self.unRedo:
            self.RMenu.add_separator()
            addcmd(
                label=_("Undo"),
                accelerator="Ctrl+Z",
                command=lambda: root.event_generate("<Control-z>"),
            )
            addcmd(
                label=_("Redo"),
                accelerator="Ctrl+Y",
                command=lambda: root.event_generate("<Control-y>"),
            )

    def _open_menu(self, event=None):
        try:
            self.RMenu.post(event.x_root, event.y_root)
        finally:
            self.RMenu.grab_release()

    # Add menu item commands
    def addMenucmd(self, label: str, acc: str = None, fn: object = None, **kw):
        return self.RMenu.add_command(label=label, accelerator=acc, command=fn, **kw)

    def addMenusepr(self):
        return self.RMenu.add_separator()

    def addMenucheckbtn(
        self, label: str, variable: BooleanVar, fn: object, acc: str = None, **kw
    ):
        return self.RMenu.add_checkbutton(
            label=label, accelerator=acc, variable=variable, command=fn, **kw
        )

    def addMenuradiobtn(
        self, label: str, variable: BooleanVar, fn: object, acc: str = None, **kw
    ):
        return self.RMenu.add_radiobutton(
            label=label, accelerator=acc, variable=variable, command=fn, **kw
        )

    def addMenucascade(self, label: str, menu: Menu, **kw):
        return self.RMenu.add_cascade(label=label, menu=menu, **kw)

    # Wrap mode
    def wrapmode(self, event=None) -> bool:
        if self.wrapbtn.get() == True:
            self.configure(wrap="none")
            self.wrapbtn.set(False)
            return False
        else:
            self.configure(wrap="word")
            self.wrapbtn.set(True)
            return True
