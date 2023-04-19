"""
@package libtextworker.interface.tk
Contains classes for Tkinter.
"""
import threading
import typing
from libtextworker import Importable
from ..manager import ColorManager, default_configs

if Importable["tkinter"] == True:
    import darkdetect
    import sv_ttk
    from tkinter import TclError, font, messagebox

    pass
else:
    raise Exception(
        "interface.tk is called but its dependency Tkinter is not installed"
    )


class ColorManager(ColorManager):
    recursive_configure: bool = True
    is_shown: bool = False  # Messages

    def _get_font(self):
        size, style, weight, family = super()._get_font()
        font_families = font.families()

        if family == "default":
            family = "Consolas"
        elif family not in font_families:
            if not self.is_shown:
                messagebox.showwarning(
                    message=_(
                        """
                        It seemed that your preferred font family does not available on your machine here.\n
                        Install the font first - and now the program will use Consolas instead.\n
                        If you think that this is a mistake, please report it.
                        """
                    )
                )
                self.is_shown = True

        if style == "normal" or style != "italic":
            style = "roman"
        return font.Font(None, family=family, weight=weight, slant=style, size=size)

    def setfontcfunc(self, objname: str, func: typing.Callable, params: dict):
        raise NotImplementedError

    def setcolorfunc(self, objname: str, func: typing.Callable, params: dict):
        raise NotImplementedError

    def configure(self, widget: typing.Any, childs_too: bool = recursive_configure):
        back, fore = self.GetColor
        font_to_use = self.GetFont

        try:
            widget.configure(font=font_to_use)
        except TclError:
            pass

        # Why this catch?
        # Some Tkinter objects do not use fg and bg as their configure() keywords,
        # but use foreground and background instead.
        try:
            widget.configure(fg=fore, bg=back)
            widget.configure(foreground=fore, background=back)
        except TclError:
            pass

        self.autocolor_run(widget)

        if childs_too:
            for child in widget.winfo_children():
                self.configure(child, self.recursive_configure)
                self.autocolor_run(child)

    def autocolor_run(self, widget: typing.Any):
        def _configure(theme: str):
            sv_ttk.set_theme(theme.lower())
            self.configure(widget)

        if self.getkey("color", "autocolor") == True or "yes":
            if widget not in self.threads or not self.threads[widget].is_alive():
                self.threads[widget] = threading.Thread(
                    target=darkdetect.listener, args=(_configure,), daemon=True
                )
                self.threads[widget].start()
            sv_ttk.set_theme(
                darkdetect.theme().lower()
            )  # Keep this to avoid 'font already exists' error


clrmgr = ColorManager(default_configs)
