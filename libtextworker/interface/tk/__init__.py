"""
@package libtextworker.interface.tk
Contains class(es) and needed attributes for Tkinter.
"""
import threading
import typing
from libtextworker import Importable
from ..manager import ColorManager

if Importable["tkinter"] == True:
    import darkdetect
    import sv_ttk
    from tkinter import TclError, font
else:
    raise Exception(
        "interface.tk is called but its dependency Tkinter is not installed.\n"
        "You'll need:\n- tkinter\n- darkdetect\n- sv-ttk\npackages."
    )


class ColorManager(ColorManager):
    recursive_configure: bool = True
    is_shown: bool = False  # Messages

    def _get_font(self):
        size, style, weight, family = super()._get_font()
        font_families = font.families()

        print(family)

        if family == "default" or family not in font_families:
            family = "Consolas"

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


## @deprecated On version 0.1.3
clrmgr = None
