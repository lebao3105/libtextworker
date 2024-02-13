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

from .. import THEMES_DIR
from ..general import logger, CraftItems
from ..get_config import ConfigurationError, GetConfig
from ..interface import stock_ui_configs, colors

try:
    import darkdetect
except ImportError as e:
    logger.exception(e.msg)
    AUTOCOLOR = False
else:
    AUTOCOLOR = bool(darkdetect.theme())

def hextorgb(value: str):
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))

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
      (excluding the self parameter if any) is for the widget, the second one is for the color.
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
        assert len(sig.parameters) > 0

        this.Target = Target
        this.Func = Func

        this.thread = threading.Thread(target=darkdetect.listener,
                                       args=(this.configure,), daemon=True)
        this.thread.start()

    def configure(this, color: str):
        color = color.lower()
        return this.Func(this.Target, color)


class ColorManager(GetConfig):
    """
    A color manager for GUI widgets.
    ColorManager can be used for multiple GUI widgets with only one call
    """

    setcolorfn: dict[object | type, list] = {}
    setfontfn: dict[object | type, list] = {}
    setfcfn: dict[object | type, list] = {}

    _threads: dict[object, threading.Thread] = {}

    def __init__(self, default_configs: dict[str, typing.Any] = stock_ui_configs,
                 customfilepath: str = CraftItems(THEMES_DIR, "default.ini")):
        """
        Constructor of the class.
        @param default_configs (dict[str]): Defaults to dev-premade configs
        @param customfilepath (str): Custom file path. Disabled by default.
        """
        if customfilepath != "":
            self._file = os.path.normpath(customfilepath)
        else:
            self._file = CraftItems(THEMES_DIR, "default.ini")

        GetConfig.__init__(self, default_configs, self._file)

        if os.path.exists("mergelist.json"):
            self.move(json.loads(open("mergelist.json", "r").read()))

    def reset(self, restore: bool = False):
        """
        Reset the configuration file.
        This is blocked as it can make conflicts with other instances of the class - unless you shutdown the app immediately..
        """
        raise NotImplementedError("reset() is blocked on ColorManager."
                                  "Please use get_config.GetConfig class instead.")

    # Configure widgets
    def GetFont(self) -> typing.Any | tuple[str, int, str, str, str]:
        """
        Call the font definitions.
        When called, this returns the following:
            (font) size (int), style, weight, family
        The output will vary on different GUI toolkits:
        * wxPython: wx.Font object
        * Tkinter: tkinter.font.Font object
        """

        if not self.has_section("font"):
            return 10, "system", "system", ""

        family = self.getkey("font", "family", False, True)
        size = self.getkey("font", "size", False, True)
        weight = self.getkey("font", "weight", False, True)
        style = self.getkey("font", "style", False, True)

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

    def GetColor(self, color: str | None = None) -> tuple[str, str]:
        """
        Get the current foreground/background defined in the settings.
        @since 0.1.4: Made to be a non-@property item
        @param color (str | None = None): Defaults to darkdetect's output/current setting.
        @return tuple[str, str]: Background - Foreground colors
        """
        # print(darkdetect.theme().lower())
        if not color:
            if AUTOCOLOR: currmode = darkdetect.theme().lower()
            else: currmode = str(self.getkey("color", "background", True, True)).lower()
        else:
            currmode = color

        # print(currmode)
        if not currmode in ["dark", "light"]:
            raise ConfigurationError(self._file, "Invalid value", "color", "background")

        # Prefer color for specific modes first
        try:
            test_back = self.getkey("color", "background-%s" % currmode, noraiseexp=True)
            test_fore = self.getkey("color", "foreground-%s" % currmode, noraiseexp=True)
            # print(test_back, test_fore)

            back_ = test_back if test_back else colors[currmode]

            fore_ = self.getkey("color", "foreground", make=True)
            if fore_ == "default":
                fore_ = colors[{"light": "dark", "dark": "light"}.get(currmode)]

            if test_fore:
                fore_ = test_fore

            elif fore_.startswith("#"):  # hex colors. TODO: rgb support?
                pass

            elif fore_ in colors:
                fore_ = colors[fore_]

            elif test_fore in colors:
                fore_ = colors[test_fore]

            else:
                raise ConfigurationError(self._file, "Invalid value", "color", "foreground")

            return back_, fore_
        except KeyError or ConfigurationError:
            pass

    def setcolorfunc(self, obj: type | object, func: typing.Callable | str, params: dict | tuple | None = None):
        """
        Set GUI widget background color-set function.
        @param obj (type | object): Object (variable or type reference)
        @param func (callable | str): Target function (no arg)
        @param params (tuple | dict): Parameters to pass to func

        Function paramers must have %(color) in order to
            pass color value. Use %(color-rgb) if you want RGB value.
        """
        if not obj in self.setcolorfn: self.setcolorfn[obj] = []
        self.setcolorfn[obj].append({"fn": func, "params": params})

    def setfontcfunc(self, obj: type | object, func: typing.Callable, params: dict | tuple | None = None):
        """
        Set GUI widget font color-set function.
        @param obj (type | object): Object (variable or type reference)
        @param func (callable | str): Function to set the font style (no arg)
        @param params (tuple | dict): Parameters to pass to func

        Function paramers must have %(font) in order to
            pass color value. Use %(font-rgb) if you want RGB value.
        """
        if not obj in self.setfontfn: self.setfontfn[obj] = []
        self.setfontfn[obj].append({"fn": func, "params": params})

    def setfontandcolorfunc(self, obj: type | object, func: typing.Callable | str, params: dict | tuple | None = None):
        """
        Add a function that sets both the background and font color.
        @param obj (type | object): Object (variable or type reference)
        @param func (typing.Callable | str): Function to use (Reference)
        @param params (typle | dict): Function parameters
        @since 0.1.4: First appearance
        """
        if not obj in self.setfcfn: self.setfcfn[obj] = []
        self.setfcfn[obj].append({"fn": func, "params": params})

    def configure(self, widget: object, color: str | None = None):
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
            self._threads.pop(widget, None)
            return

        color, fontcolor = self.GetColor(color)

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
                # BUG: Not working? (tested on wx)
                temp = list(args)
                for arg in temp:
                    if isinstance(arg, str):
                        arg = replacetext(arg)
                args = tuple(temp)
                return func(*args)
        
        def runloop(attr: typing.Literal["color", "font", "fc"]):

            for item in getattr(self, f"set{attr}fn"):
                if isinstance(item, type):
                    if not isinstance(widget, item): continue
                elif item != widget: continue

                dictionary = getattr(self, f"set{attr}fn")[item]

                for i in range(len(dictionary)):
                    fn = getattr(self, f"set{attr}fn")[item][i]["fn"]
                    if isinstance(fn, str): fn = getattr(widget, fn)

                    runfn(fn, dictionary[i]["params"])

        runloop("color")
        runloop("font")
        runloop("fc")

    def autocolor_run(self, widget: typing.Any):
        autocolor = self.getkey("color", "auto")
        if (not AUTOCOLOR) or (autocolor in self.no_values):
            logger.warning("ColorManager.autocolor_run() called when auto-color system is not usable."
                           "Detailed: auto coloring has been turned of or doesn't have required dependency (darkdetect).")
            return

        self._threads[widget] = UISync(widget, self.configure)
