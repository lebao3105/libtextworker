"""
@package libtextworker.interface.manager
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import json
import os
import typing
import threading

from .. import THEMES_DIR, Importable
from ..general import logger, CraftItems
from ..get_config import ConfigurationError, GetConfig
from ..interface import stock_ui_configs, colors

if Importable['darkdetect']:
    import darkdetect
    AUTOCOLOR = darkdetect.theme() is not None
else:
    AUTOCOLOR = False

def hextorgb(value: str):
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgbtohex(value: str):
    return "#{:02x}{:02x}{:02x}".format(eval(value))

class UISync:
    """
    A class that automatically syncs your UI to match system settings.

    Why UISync:
    * The original ColorManager.autocolor_run, which just makes a thread running ColorManager.configure, does not work.
    * Easy to use, quick setup. No need to derive this class!
    * I've looked for solutions from older builds of texteditor/textworker, found that v1.4
    uses a custom class. So I made this:)

    Notes:
    * The target function that will be used must accept at least arguments, with the first one
      (excluding the class's this/self parameter if any) is for the widget, the second one is for the color.
    * Nothing more (for now)

    Don't get this class wrong: This only makes a thread that uses your custom function.
    """

    Target: object
    Func: typing.Callable | type

    def __init__(this, Target: object, Func: typing.Callable | type):
        # Nothing is allowed to be None
        assert Target != None
        assert Func != None

        # Target function must accept arguments
        from inspect import signature
        sig = signature(Func)
        assert len(sig.parameters) > 0, "Used function has no parameter, must be at least 2"

        this.Target = Target
        this.Func = Func

        this.thread = threading.Thread(target=darkdetect.listener,
                                       args=(this.configure,), daemon=True)
        this.thread.start()

    def configure(this, color: str):
        return this.Func(this.Target, color.lower())


class ColorManager(GetConfig):
    """
    A color manager for GUI widgets.
    """

    setcolorfn: dict[object | type, list] = {}
    setfontfn: dict[object | type, list] = {}
    setfcfn: dict[object | type, list] = {}

    _threads: dict[object, threading.Thread] = {}

    # Configure widgets
    def GetFont(this) -> typing.Any | tuple[int, str, str, str]:
        """
        Call the font definitions.
        When called, this returns the following:
            (font) size (int), style, weight, family
        The output will vary on different GUI toolkits:
        * wxPython: wx.Font object
        * Tkinter: tkinter.font.Font object
        """

        if not this.has_section("font"):
            return 10, "system", "system", ""

        family = this.Get("font", "family", find_everywhere=True, noraise=True)
        size = this.Get("font", "size", find_everywhere=True, noraise=True)
        weight = this.Get("font", "weight", find_everywhere=True, noraise=True)
        style = this.Get("font", "style", find_everywhere=True, noraise=True)

        if family == "default":
            family = ""

        try:
            int(size)
        except ValueError:
            size_ = 10
        else:
            if int(size) > 0:
                size_ = int(size)
            else:
                raise ValueError("Font size must be higher than 0")

        return size_, style, weight, family

    def GetColor(this, color: str | None = None) -> tuple[str, str]:
        """
        Get the current foreground/background defined in the settings.
        @since 0.1.4: Made to be a non-@property item
        @param color (str | None = None): Defaults to darkdetect's output/current setting.
        @return tuple[str, str]: Background - Foreground colors
        """

        if not color:
            if AUTOCOLOR: currmode = darkdetect.theme().lower()
            else: currmode = str(this.Get("color", "background", True, True)).lower()
        else:
            currmode = color

        if not currmode in ["dark", "light"]:
           raise ConfigurationError(this._file, "Invalid value", "color", "background", currmode)

        # Prefer color for specific modes first
        if f"background-{currmode}" in this["color"]:
            test_back = this.Get("color", f"background-{currmode}")
            back_ = test_back if test_back else colors[currmode]

        fore_ = this.Get("color", "foreground", find_everywhere=True, noraise=True)
        if fore_ == "default":
            fore_ = colors[{"light": "dark", "dark": "light"}.get(currmode, "dark")]

        if f"foreground-{currmode}" in this["color"]:
            if test_fore := this.Get("color", f"foreground-{currmode}"):
                fore_ = test_fore

        if fore_.startswith("#"):
            pass

        elif fore_ in colors:
            fore_ = colors[fore_]

        elif test_fore in colors:
            fore_ = colors[test_fore]

        else:
            fore_ = rgbtohex(fore_) # RGB to hex
            raise ConfigurationError(this._file, "Invalid value", "color", "foreground", fore_)

        return back_, fore_

    def setcolorfunc(this, obj: type | object, func: typing.Callable | str, params: dict | tuple | None = None):
        """
        Set GUI widget background color-set function.
        @param obj (type | object): Object (variable or type reference)
        @param func (callable | str): Target function (no arg)
        @param params (tuple | dict): Parameters to pass to func

        Function paramers must have %(color) in order to
            pass color value. Use %(color-rgb) if you want RGB value.
        """
        if not obj in this.setcolorfn: this.setcolorfn[obj] = []
        this.setcolorfn[obj].append({"fn": func, "params": params})

    def setfontcfunc(this, obj: type | object, func: typing.Callable, params: dict | tuple | None = None):
        """
        Set GUI widget font color-set function.
        @param obj (type | object): Object (variable or type reference)
        @param func (callable | str): Function to set the font style (no arg)
        @param params (tuple | dict): Parameters to pass to func

        Function paramers must have %(font) in order to
            pass color value. Use %(font-rgb) if you want RGB value.
        """
        if not obj in this.setfontfn: this.setfontfn[obj] = []
        this.setfontfn[obj].append({"fn": func, "params": params})

    def setfontandcolorfunc(this, obj: type | object, func: typing.Callable | str, params: dict | tuple | None = None):
        """
        Add a function that sets both the background and font color.
        @param obj (type | object): Object (variable or type reference)
        @param func (typing.Callable | str): Function to use (Reference)
        @param params (typle | dict): Function parameters
        @since 0.1.4: First appearance
        """
        if not obj in this.setfcfn: this.setfcfn[obj] = []
        this.setfcfn[obj].append({"fn": func, "params": params})

    def configure(this, widget: object, color: str | None = None):
        """
        Style a widget (only fore+back) with pre-defined settings.
        This is usable for (almost) all GUI toolkits.

        @param widget : Widget to configure
        @param color: Color to use (optional)
        @see setcolorfunc
        @see setfontcfunc
        """

        if not widget:
            logger.debug(f"Widget {widget} died, skip configuring.")
            this._threads.pop(widget, None)
            return

        color, fontcolor = this.GetColor(color)

        def runfn(func: typing.Callable, args: dict|tuple):
            extra_aliases = {
                "%(color)": color,
                "%(font)": fontcolor
            }

            def replacetext(target: str):
                for key in extra_aliases:
                    target = target.replace(key, extra_aliases[key])
                return target

            if isinstance(args, dict):
                for key in args:
                    if isinstance(args[key], str):
                        args[key] = replacetext(args[key])
                return func(**args)
            
            elif isinstance(args, tuple):
                temp = list(args)
                for i in range(len(temp)):
                    arg = temp[i]
                    if isinstance(arg, str):
                        temp[i] = replacetext(arg)
                args = tuple(temp)
                return func(*args)
        
        def runloop(attr: typing.Literal["color", "font", "fc"]):

            for item in getattr(this, f"set{attr}fn"):
                if isinstance(item, type):
                    if not isinstance(widget, item): continue
                elif item != widget: continue

                dictionary = getattr(this, f"set{attr}fn")[item]

                for i in range(len(dictionary)):
                    fn = dictionary[i]["fn"]
                    if isinstance(fn, str): fn = getattr(widget, fn)

                    runfn(fn, dictionary[i]["params"])

        runloop("color")
        runloop("font")
        runloop("fc")

    def autocolor_run(this, widget: typing.Any):
        """
        Creates and runs a thread that automatically color a widget if able.

        @param widget: Target object
        """
        autocolor = this.Get("color", "auto")
        if (not AUTOCOLOR) or (autocolor in this.no_values):
            logger.warning("ColorManager.autocolor_run() called when auto-color system is not usable."
                           "Detailed: auto coloring has been turned of or doesn't have required dependency (darkdetect).")
            return

        this._threads[widget] = UISync(widget, this.configure)
