"""
@package libtextworker.interface.tk
Contains class(es) and needed attributes for Tkinter.
"""
import threading
from tkinter import Menu
import typing
from ... import Importable
from ..manager import ColorManager, AUTOCOLOR

if Importable["tkinter"] == True:
    from tkinter import TclError, font, Misc
else:
    raise Exception(
        "interface.tk is called but its dependencies are not installed.\n"
        "You'll need:\n- tkinter\n- darkdetect (optional)\n- sv-ttk (optional)\npackages."
    )

try:
    import sv_ttk
except ImportError:
    SVTTK_AVAILABLE = False
else:
    SVTTK_AVAILABLE = True

if AUTOCOLOR:
    import darkdetect
else:
    pass


class ColorManager(ColorManager):
    recursive_configure: bool = True
    is_shown: bool = False  # Messages

    def _get_font(self):
        size, style, weight, family = super()._get_font()
        font_families = font.families()

        if family == "default" or family not in font_families:
            family = "Consolas"

        if style == "normal" or style != "italic":
            style = "roman"

        if weight == "system":
            weight = "normal"

        if weight not in ["system", "normal", "bold"]:
            # from warnings import warn
            # warn("Tkinter font weight must be 'normal', 'system' (an alias to 'normal') or 'bold'")
            weight = "normal"

        return font.Font(None, family=family, weight=weight, slant=style, size=size)

    def setfontcfunc(self, objname: str, func: typing.Callable, params: dict):
        raise NotImplementedError

    def setcolorfunc(self, objname: str, func: typing.Callable, params: dict):
        raise NotImplementedError

    def configure(self, widget: Misc, childs_too: bool = recursive_configure):
        back, fore = self.GetColor
        font_to_use = self._get_font()

        if "Menu" in widget.winfo_class():
            font_to_use.configure(size=10)
            for i in range(0, int(widget.index("end"))):
                widget.entryconfigure(i, background=back)

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

        if childs_too:
            for child in widget.winfo_children():
                self.configure(child, True)

    def autocolor_run(self, widget: typing.Any):
        def _configure(theme: str = ""):
            if not theme:
                theme = self.getkey("color", "background", True, True, True)
            if SVTTK_AVAILABLE:
                sv_ttk.set_theme(theme.lower())
            self.configure(widget)

        if self.getkey("color", "auto") in self.yes_values:
            threading.Thread(
                target=darkdetect.listener, args=(_configure,), daemon=True
            ).start()

            if SVTTK_AVAILABLE:  # To avoid 'font already exists' error
                if not AUTOCOLOR:
                    sv_ttk.set_theme(
                        self.getkey("color", "background", True, True, True)
                    )
                else:
                    sv_ttk.set_theme(darkdetect.theme().lower())
