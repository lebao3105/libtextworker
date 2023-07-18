import json
import os
import typing
import threading

try:
    import darkdetect
except ImportError:
    AUTOCOLOR = False
else:
    if darkdetect.theme() is None:  # Unsupported OS
        AUTOCOLOR = False
    else:
        AUTOCOLOR = True

from .. import THEMES_DIR
from ..general import logger, libTewException, CraftItems, logger
from ..get_config import ConfigurationError, GetConfig
from ..interface import stock_ui_configs, colors

if AUTOCOLOR is False:
    logger.warning("GUI auto-color is not usable")


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
        customfilepath: str = "",
    ):
        """
        Constructor of the class.
        @param default_configs (dict[str, Any]): Defaults to dev-premade configs
        @param customfilepath (str): Custom file path. Set to "" (default) to disable it.
        """
        if customfilepath != "":
            self._file = os.path.abspath(customfilepath)
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
            "reset() is blocked on ColorManager. Please use get_config.GetConfig class instead."
        )

    def backup(self, file: str):
        """
        Backup a file to another file
        @param file : str : Target backup file
        """
        if file == self._file:
            raise libTewException(
                "Unusable parameter value: file must not equal ColorManager._file"
            )

        with open(file, "w") as f:
            self.write(f)

    # Configure widgets
    @property
    def GetFont(self) -> typing.Any:
        """
        Property of ColorManager to call the font definitions.
        When called, this returns the following:
            (font) size (int|str), style, weight, family
        The output will vary on different GUI toolkits:
        * wxPython: wx.Font object
        * Tkinter: tkinter.font.Font object
        """
        return self._get_font()

    @GetFont.setter
    def GetFont(self, func: typing.Callable):
        self._get_font = func

    @GetFont.deleter
    def GetFont(self):
        self._get_font = print("ColorManager.GetFont | _get_font died")

    def _get_font(self):
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

    @property
    def GetColor(self) -> typing.Any:
        """
        Property of ColorManager to call the color definitions.
        When called, it returns the following:
            background color, foreground color (in hex-rgb format)
        """
        return self._get_color()

    @GetColor.setter
    def GetColor(self, func: typing.Callable):
        self._get_color = func

    @GetColor.deleter
    def GetColor(self):
        self._get_color = print("ColorManager.GetColor | _get_color died")

    def _get_color(self):
        # Deternmine if we can use darkdetect here
        if AUTOCOLOR:
            currmode = darkdetect.theme().lower()
        else:
            currmode = str(self.getkey("color", "background", restore=True)).lower()

        if not currmode in ["dark", "light"]:  # This for the value infile
            raise ConfigurationError(self._file, "Invalid value", "color", "background")

        # Prefer color for specific modes first
        test_back = self.getkey("color", "background-%s" % currmode, noraiseexp=True)
        test_fore = self.getkey("color", "foreground-%s" % currmode, noraiseexp=True)
        # print(test_back, test_fore)
        if test_back:
            back_ = test_back
        else:
            back_ = colors[currmode]

        fore_ = self.getkey("color", "foreground", restore=True)
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

    def setcolorfunc(self, objname: str, func: typing.Callable, params: dict | tuple):
        """
        Set GUI widget background color-set function.
        @param objname (str): Object name (for easier access)
        @param func (callable): Target function (no arg)
        @param params: Parameters to pass to

        Function paramers must have %(color) in order to
            pass color value. Use %(color-rgb) if you want RGB value.
        """
        self.setcolorfn[objname] = {"fn": func, "params": params}

    def setfontcfunc(self, objname: str, func: typing.Callable, params: dict | tuple):
        """
        Set GUI widget font color-set function.
        @param objname (str): Object name (for easier access)
        @param func (callable): Function to set the font style (no arg)
        @param params: Parameters to pass to func

        Function paramers must have %(font) in order to
            pass color value. Use %(font-rgb) if you want RGB value.
        """
        self.setfontfn[objname] = {"fn": func, "params": params}

    def configure(self, widget: typing.Any):
        """
        Style a widget (only fore+back) with pre-defined settings.
        This is usable for (almost) all GUI toolkits.

        @param widget : Widget to configure
        @see setcolorfunc
        @see setfontcfunc
        """

        def runfn(
            args: tuple | dict,
            extra: str = "",
            extra_alias: str = "",
            fn: typing.Callable | None = None,
        ) -> dict | tuple | None:
            FOUND: bool = False

            if isinstance(args, tuple):
                if fn:
                    return fn(*args)
                for item in args:
                    if isinstance(item, str) and item == extra_alias:
                        FOUND = True
                        args[args.index(item)] = extra

            elif isinstance(args, dict):
                if fn:
                    return fn(**args)

                for item in args:
                    if isinstance(args[item], str) and args[item] == extra_alias:
                        FOUND = True
                        args[item] = extra

            return args if FOUND else None

        if not widget:
            logger.debug(f"Widget {widget} died, skip configuring.")
            return

        color, fontcolor = self.GetColor

        for item in self.setfontfn:
            fn = self.setfontfn[item]["fn"]
            if not self.setfontfn[item]["params"]:
                fn(fontcolor)
            else:
                args = runfn(
                    args=self.setfontfn[item]["params"],
                    extra=fontcolor,
                    extra_alias="%(font)",
                )
                if not args:
                    args = runfn(
                        args=self.setfontfn[item]["params"],
                        extra=tuple(
                            int(fontcolor.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
                        ),
                        extra_alias="%(font-rgb)",
                    )
                runfn(fn=fn, args=args)

        for item in self.setcolorfn:
            fn = self.setcolorfn[item]["fn"]
            if not self.setcolorfn[item]["params"]:
                fn(color)
            else:
                args = runfn(
                    args=self.setcolorfn[item]["params"],
                    extra=color,
                    extra_alias="%(color)",
                )
                if not args:
                    args = runfn(
                        args=self.setcolorfn[item]["params"],
                        extra=tuple(
                            int(color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
                        ),
                        extra_alias="%(color-rgb)",
                    )
                runfn(fn=fn, args=args)

    def autocolor_run(self, widget: typing.Any):
        autocolor = self.getkey("color", "auto")
        if not AUTOCOLOR:
            logger.info(
                "ColorManager.autocolor_run() called when auto-color system is not usable. Skipping."
            )

        if autocolor in self.yes_values:
            threading.Thread(args=self.configure(widget), daemon=True).start()
