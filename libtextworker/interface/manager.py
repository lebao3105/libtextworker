import json
import os
import typing
import threading

try:
    import darkdetect
except ImportError:
    AUTOCOLOR = False
else:
    AUTOCOLOR = bool(darkdetect.theme())

from .. import THEMES_DIR
from ..general import logger, CraftItems
from ..get_config import ConfigurationError, GetConfig
from ..interface import stock_ui_configs, colors

if AUTOCOLOR is False:
    logger.warning("GUI auto-color is not usable")


def hextorgb(value: str):
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))


class ColorManager(GetConfig):
    """
    A color manager for GUI widgets.
    ColorManager can be used for multiple GUI widgets with only one call
    """

    setcolorfn = {}
    setfontfn = {}

    def __init__(
        self,
        default_configs: dict[str, typing.Any] = stock_ui_configs,
        customfilepath: str = CraftItems(THEMES_DIR, "default.ini"),
    ):
        """
        Constructor of the class.
        @param default_configs (dict[str, Any]): Defaults to dev-premade configs
        @param customfilepath (str): Custom file path. Disabled by default.
        """
        if customfilepath != "":
            self._file = os.path.normpath(customfilepath)
        else:
            self._file = CraftItems(THEMES_DIR, "default.ini")

        super().__init__(default_configs, self._file)

        if os.path.exists("mergelist.json"):
            self.move(json.loads(open("mergelist.json", "r").read()))

    def reset(self, restore: bool = False):
        """
        Reset the configuration file.
        This is blocked as it can make conflicts with other instances of the class - unless you shutdown the app immediately..
        """
        raise NotImplementedError(
            "reset() is blocked on ColorManager. Please use get_config.GetConfig class instead.\n"
            "However, I'm thinking about opening it back;-;"
        )

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
        @param color (str | None = None): Defaults to darkdetect's output/current config.
        @return tuple[str, str]: Background - Foreground color
        """

        # Deternmine if we can use darkdetect here
        if AUTOCOLOR and color is None:
            currmode = darkdetect.theme().lower()
        elif not AUTOCOLOR and color is None:
            currmode = str(
                self.getkey("color", "background", needed=True, make=True)
            ).lower()
        else:
            currmode = color

        # if not currmode in ["dark", "light"]:
        #     raise ConfigurationError(self._file, "Invalid value", "color", "background")

        # Prefer color for specific modes first
        try:
            test_back = self.getkey(
                "color", "background-%s" % currmode, noraiseexp=True
            )
            test_fore = self.getkey(
                "color", "foreground-%s" % currmode, noraiseexp=True
            )
            # print(test_back, test_fore)

            if test_back:
                back_ = test_back
            else:
                back_ = colors[currmode]

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
                raise ConfigurationError(
                    self._file, "Invalid value", "color", "foreground"
                )

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
        self.setcolorfn[obj] = {"fn": func, "params": params}

    def setfontcfunc(self, obj: type | object, func: typing.Callable, params: dict | tuple | None = None):
        """
        Set GUI widget font color-set function.
        @param obj (type | object): Object (variable or type reference)
        @param func (callable | str): Function to set the font style (no arg)
        @param params (tuple | dict): Parameters to pass to func

        Function paramers must have %(font) in order to
            pass color value. Use %(font-rgb) if you want RGB value.
        """
        self.setfontfn[obj] = {"fn": func, "params": params}

    def configure(self, widget: typing.Any):
        """
        Style a widget (only fore+back) with pre-defined settings.
        This is usable for (almost) all GUI toolkits.

        @param widget : Widget to configure
        @see setcolorfunc
        @see setfontcfunc
        """

        def runfn(func: typing.Callable, args: dict|tuple, extra: str, extra_alias: str):

            if isinstance(args, dict):
                for key in args:
                    if isinstance(args[key], str):
                        args[key] = args[key].replace(extra_alias, extra)
                return func(**args)
            
            elif isinstance(args, tuple):
                temp = list(args)
                for arg in temp:
                    if isinstance(arg, str):
                        arg = arg.replace(extra_alias, extra)
                args = tuple(temp)
                return func(*args)
        

        if not widget:
            logger.debug(f"Widget {widget} died, skip configuring.")
            return

        color, fontcolor = self.GetColor()
        
        def runloop(attr: typing.Literal["color", "font"]):
            for item in getattr(self, f"set{attr}fn"):
                if isinstance(item, type):
                    if not isinstance(widget, item): continue
                elif item != widget: continue
                fn = getattr(self, f"set{attr}fn")[item]["fn"]
                if isinstance(fn, str): fn = getattr(widget, fn)
                runfn(fn, getattr(self, f"set{attr}fn")[item]["params"],
                      fontcolor if attr == "font" else color, f"%({attr})")

        runloop("color")
        runloop("font")

    def autocolor_run(self, widget: typing.Any):
        autocolor = self.getkey("color", "auto")
        if not AUTOCOLOR:
            logger.info(
                "ColorManager.autocolor_run() called when auto-color system is not usable. Skipping."
            )

        if autocolor in self.yes_values:
            threading.Thread(args=self.configure(widget), daemon=True).start()
