import json
import os
import typing
import threading

try:
    import darkdetect
except ImportError:
    AUTOCOLOR = False
else:
    if darkdetect.theme() is None:
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
        customfilepath: str = ""
    ):
        """
        Constructor of the class.
        @param default_configs (dict[str, Any]): Defaults to dev-premade configs
        @param customfilepath (str): Custom file path. Set to "" (default) to disable it.
        """
        if isinstance(customfilepath, str) and customfilepath != "":
            self._file = customfilepath
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
    def GetFont(self):
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
    def GetColor(self):
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
        def _get_sys_mode():
            return darkdetect.theme().lower()

        # Get values
        color = self.getkey("color", "background", False, True)
        fontcolor = self.getkey("color", "foreground", False, True)
        autocolor = self.getkey("color", "auto", False, True)

        ##
        resv = {"light": "dark", "dark": "light"}

        ## Check
        if autocolor in self.yes_values and AUTOCOLOR is True:
            color_ = colors[_get_sys_mode()]
        else:
            color_ = colors[color]

        # Text color
        if fontcolor == "default":
            if autocolor not in self.yes_values or AUTOCOLOR is False:
                fontcolor_ = colors[resv[color]]
                
            elif autocolor in self.yes_values and AUTOCOLOR is True:
                fontcolor_ = colors[resv[_get_sys_mode()]]

        elif fontcolor in colors:
            fontcolor_ = colors[fontcolor]

        else:
            raise ConfigurationError(
                "interface", "textcolor", "Invalid color name/code"
            )

        return color_, fontcolor_

    def setcolorfunc(self, objname: str, func: typing.Callable, params: dict|tuple):
        """
        Set GUI widget background color-set function.
        @param objname (str): Object name (for easier access)
        @param func (callable): Target function (no arg)
        @param params: Parameters to pass to

        Function paramers must have %(color) in order to
            pass color value.
        """
        self.setcolorfn[objname] = {"fn": func, "params": params}

    def setfontcfunc(self, objname: str, func: typing.Callable, params: dict|tuple):
        """
        Set GUI widget font color-set function.
        @param objname (str): Object name (for easier access)
        @param func (callable): Function to set the font style (no arg)
        @param params: Parameters to pass to func

        Function paramers must have %(font) in order to
            pass color value.
        """
        self.setfontfn[objname] = {"fn": func, "params": params}

    def configure(self, widget: typing.Any):
        """
        Style a widget (only fore+back) with pre-defined settings.
        @param widget : Widget to configure
        @see setcolorfunc
        @see setfontcfunc
        """

        def runfn(func, args, extra, extra_alias: str):
            if isinstance(args, tuple):
                for item in args:
                    if isinstance(item, str) and item == extra_alias:
                        args[args.index(item)] = extra
                func(*args)

            elif isinstance(args, dict):
                for item in args:
                    if isinstance(args[item], str) and args[item] == extra_alias:
                        args[item] = extra
                func(**args)

        if not widget:
            logger.debug(f"Widget {widget} died, skip configuring.")
            return

        color, fontcolor = self.GetColor

        for item in self.setfontfn:
            fn = self.setfontfn[item]["fn"]
            if not self.setfontfn[item]["params"]:
                fn(fontcolor)
            else:
                runfn(fn, self.setfontfn[item]["params"], fontcolor, "%(font)")

        for item in self.setcolorfn:
            fn = self.setcolorfn[item]["fn"]
            if not self.setcolorfn[item]["params"]:
                fn(color)
            else:
                runfn(fn, self.setcolorfn[item]["params"], color, "%(color)")

    def autocolor_run(self, widget: typing.Any):
        autocolor = self.getkey("color", "auto")
        if not AUTOCOLOR:
            raise Exception("ColorManager.autocolor_run() called when auto-color system is not usable")
        
        if autocolor in self.yes_values:
            threading.Thread(
                args=self.configure(widget), daemon=True
            ).start()
