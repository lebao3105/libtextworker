import configparser
import os
import pathlib
import threading

import darkdetect
import wx
from PIL import ImageColor
# from pygments.lexers import guess_lexer

from .. import Importable
from ..general import CraftItems, libTewException
from ..get_config import ConfigurationError, GetConfig
from . import constants

LANGS_DIR = CraftItems(pathlib.Path(__file__).parent, "../syntaxhighlight")
THEMES_DIR = os.path.expanduser("~/.config/libtew/themes/")

# TODO: Resolve conflicts with ColorManager
# class LanguageHighlight(configparser.ConfigParser):
    
#     def LanguageInit(self, text:str):
#         language = guess_lexer(text).__module__.removeprefix("pygments.lexers.").removesuffix("Lexer")
#         target = CraftItems(LANGS_DIR, language.lower() + ".ini")
#         print(target)
#         self.read(target)

#         # Required sections
#         for section in ['project', 'highlight', 'keywords']:
#             if not self.has_section(section):
#                 raise ConfigurationError(section, msg="Section not found")
            
#         self.progname = self["project"]["name"]
#         self.fileexts = self["project"]["file_extensions"].split()

#     def InitializeUIType(self):
#         if not Importable["interface.wx"]:
#             raise libTewException("Unable to use wx")
        
#         import wx.stc
#         if not self.has_section("wxSTC"):
#             raise ConfigurationError("wxSTC", msg="Section not found")
            
#         if not hasattr(wx.stc, 'STC_LEX_{}'.format(self.get("wxSTC", "lexer_suffix").replace("'", ''))):
#             raise libTewException("Sorry about that, but wx.stc does not support {} language yet".format(self.progname))

#     def ConfigureWxWidget(self, widget):
#         import wx.stc
#         shortname = self["wxSTC"]["short_name"]
#         keywords = []
#         # Set Lexer
#         widget.SetLexer(getattr(wx.stc, "STC_LEX_PYTHON"))
#         # Set code keywords
#         for option in self["keywords"]:
#             keywords += self["keywords"][option].split('|')
#         widget.SetKeyWords(0, " ".join(keywords))
        
#         # Set highlight style
#         widget.StyleClearAll()
#         for option in self["highlight"]:
#             widget.StyleSetSpec(getattr(wx.stc, "STC_{}_{}".format(shortname, option.upper()).replace("'", '')), self["highlight"][option])


class ColorManager(GetConfig):
    setcolorfn = {}
    setfontfn = {}

    def __init__(
        self, customfilepath: str or bool = False
    ):
        if isinstance(customfilepath, str) and customfilepath != "":
            self.__file = customfilepath
        else:
            self.__file = THEMES_DIR + "default.ini"

        super().__init__({}, self.__file, default_section="colors")
    
    def reset(self, restore: bool = False):
        raise NotImplementedError("reset function is blocked on ColorManager. Please use the get_config.GetConfig class instead.")

    def backup(self, file: str):
        """
        Backup a file to another file
        """
        if file == self.__file:
            raise libTewException("Unusable parameter value: file must not equal ColorManager.__file")
        
        with open(file, "w") as f:
            self.write(f)
    
    # Configure widgets
    @property
    def GetFont(self):
        return self._get_font()

    @GetFont.setter
    def GetFont(self, func):
        self._get_font = func

    @GetFont.deleter
    def GetFont(self):
        self._get_font = print("Deleted object: GetConfig.GetFont/_get_font")

    def _get_font(self):
        family = self.get("font", "family")
        size = self.get("font", "size")
        weight = self.get("font", "weight")
        style = self.get("font", "style")

        weight_ = constants.FONTWT[weight]
        style_ = constants.FONTST[style]

        if family == "default":
            family = ""

        try:
            int(size)
        except ValueError:
            size_ = constants.FONTSZ[size]
        else:
            size_ = int(size)

        return wx.Font(size_, wx.FONTFAMILY_DEFAULT, style_, weight_, 0, family)

    @property
    def GetColor(self):
        return self._get_color()

    @GetColor.setter
    def GetColor(self, func):
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
        if autocolor == True:
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

    def setcolorfunc(self, objname: str, func, params: dict):
        """
        Set wxPython widgets background color function.
        :param objname (str): Object name (for easier access)
        :param func (function): Function to set the background color (no arg)
        :param params (dict): Parameters to pass to func
        """
        self.setcolorfn[objname] = {"fn": func, "params": params}

    def setfontcfunc(self, objname: str, func, params: dict):
        """
        Set wxPython widgets background color function.
        :param objname (str): Object name (for easier access)
        :param func (function): Function to set the background color (no arg)
        :param params (dict): Parameters to pass to func
        """
        self.setfontfn[objname] = {"fn": func, "params": params}

    def configure(self, widget):
        if not widget:
            print("Widget died, skip configuring.")
            return

        widget.SetFont(self._get_font())
        color, fontcolor = self._get_color()

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

        autocolor = self.getkey("color", "autocolor")
        if autocolor == True and widget in self.threads:
            if not self.threads[widget].is_alive():
                self.threads[widget] = threading.Thread(
                    args=self.configure(widget), daemon=True
                )
                self.threads[widget].start()