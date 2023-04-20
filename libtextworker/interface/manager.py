import typing
import threading

import darkdetect
from PIL import ImageColor

from .. import THEMES_DIR
from ..general import libTewException, CraftItems
from ..get_config import ConfigurationError, GetConfig

"""
Default UI configurations
"""
default_configs = {
    "color": {"background": "light", "autocolor": "yes", "textcolor": "default"},
    "font": {
        "style": "normal",
        "weight": "normal",
        "family": "default",
        "size": "normal",
    },
}


class ColorManager(GetConfig):
    """
    A color manager for GUI widgets.
    ColorManager reads configs from a file (default is under THEMES_DIR)
    """

    setcolorfn = {}
    setfontfn = {}
    threads = {}

    def __init__(
        self,
        default_configs: dict[str, typing.Any],
        customfilepath: str or bool = False,
    ):
        """
        Constructor of the class.
        @param default_configs (dict[str, Any]): Defaults to default_configs, this is dev-made configs
        @param customfilepath (str|bool): Custom file path support. Set to False (default) or "" to disable it.
        """
        if isinstance(customfilepath, str) and customfilepath != "":
            self.__file = customfilepath
        else:
            self.__file = CraftItems(THEMES_DIR, "default.ini")

        super().__init__(default_configs, self.__file, default_section="colors")

    def reset(self, restore: bool = False):
        """
        Reset the configuration file.
        This is blocked as it can make conflicts with other GUI widgets - unless you shutdown the app immediately..
        """
        raise NotImplementedError(
            "reset function is blocked on ColorManager. Please use the get_config.GetConfig class instead."
        )

    def backup(self, file: str):
        """
        Backup a file to another file
        @param file : str : Target backup file
        """
        if file == self.__file:
            raise libTewException(
                "Unusable parameter value: file must not equal ColorManager.__file"
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
        """
        return self._get_font()

    @GetFont.setter
    def GetFont(self, func: typing.Callable):
        self._get_font = func

    @GetFont.deleter
    def GetFont(self):
        self._get_font = print("Deleted object: GetConfig.GetFont/_get_font")

    def _get_font(self):
        family = self.get("font", "family")
        size = self.get("font", "size")
        weight = self.get("font", "weight")
        style = self.get("font", "style")

        if family == "default":
            family = ""

        try:
            int(size)
        except ValueError:
            size_ = 14
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
        self._get_color = print("Deleted object: GetConfig.GetColor/_get_color")

    def _get_color(self):
        def _get_sys_mode():
            return darkdetect.theme().lower()

        # Get values
        color = self.getkey("color", "background")
        fontcolor = self.getkey("color", "textcolor")
        autocolor = self.getkey("color", "autocolor")

        # Interface color
        ## Default color modes
        colors = {
            "light": "#ffffff",
            "dark": "#1c1c1c",
        }

        ##
        resv = {"light": "dark", "dark": "light"}

        ## Check
        if autocolor == True or "yes":
            color_ = colors[_get_sys_mode()]
        elif color in colors:
            color_ = colors[color]

        # Text color
        colors["green"] = "#00ff00"
        colors["red"] = "#ff0000"
        if fontcolor == "default":
            if autocolor == False:
                fontcolor_ = colors[resv[color]]
            else:
                fontcolor_ = colors[resv[_get_sys_mode()]]
        else:
            if fontcolor in colors:
                fontcolor_ = colors[fontcolor]
            elif fontcolor.startswith("#") and len(fontcolor) == 7:
                try:
                    ImageColor.getrgb(fontcolor)
                except ValueError:
                    raise ConfigurationError(
                        "interface", "textcolor", "Invalid color name/code"
                    )
                else:
                    fontcolor_ = fontcolor
            else:
                raise ConfigurationError(
                    "interface", "textcolor", "Invalid color name/code"
                )

        return ImageColor.getrgb(color_), ImageColor.getrgb(fontcolor_)

    def setcolorfunc(self, objname: str, func: typing.Callable, params: dict):
        """
        Set wxPython widgets background color function.
        @param objname (str): Object name (for easier access)
        @param func (callable): Function to set the background color (no arg)
        @param params (dict): Parameters to pass to func
        """
        self.setcolorfn[objname] = {"fn": func, "params": params}

    def setfontcfunc(self, objname: str, func: typing.Callable, params: dict):
        """
        Set wxPython widgets background color function.
        @param objname (str): Object name (for easier access)
        @param func (callable): Function to set the background color (no arg)
        @param params (dict): Parameters to pass to func
        """
        self.setfontfn[objname] = {"fn": func, "params": params}

    def configure(self, widget: typing.Any):
        """
        Configure a widget with pre-defined settings.
        This function also ables to rerun itself under a threading thread.
        @param widget : Widget to configure
        @see setcolorfunc
        @see setfontcfunc
        """
        if not widget:
            print("Widget died, skip configuring.")
            return

        color, fontcolor = self.GetColor

        for item in self.setfontfn:
            fn = self.setfontfn[item]["fn"]
            if not self.setfontfn[item]["params"]:
                fn(fontcolor)
            else:
                fn(self.setfontfn[item]["params"], fontcolor)

        for item in self.setcolorfn:
            fn = self.setcolorfn[item]["fn"]
            if not self.setcolorfn[item]["params"]:
                fn(color)
            else:
                fn(self.setcolorfn[item]["params"], color)

    def autocolor_run(self, widget: typing.Any):
        autocolor = self.getkey("color", "autocolor")
        if autocolor == True or "yes" and widget not in self.threads:
            self.threads[widget] = threading.Thread(
                args=self.configure(widget), daemon=True
            )
            self.threads[widget].start()
