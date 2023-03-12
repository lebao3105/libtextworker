import configparser
import pathlib

from pygments.lexers import guess_lexer
from .. import Importable
from ..general import CraftItems, libTewException
from ..get_config import ConfigurationError

LANGS_DIR = CraftItems(pathlib.Path(__file__).parent, "../syntaxhighlight")

class LanguageHighlight(configparser.ConfigParser):
    
    def LanguageInit(self, text:str):
        language = guess_lexer(text).__module__.removeprefix("pygments.lexers.").removesuffix("Lexer")
        target = CraftItems(LANGS_DIR, language.lower() + ".ini")
        self.read(target)

        # Required sections
        for section in ['project', 'highlight', 'keywords']:
            if not self.has_section(section):
                raise ConfigurationError(section, msg="Section not found")
            
        self.progname = self["project"]["name"]
        self.fileexts = self["project"]["file_extensions"].split()

    def InitializeUIType(self):
        if not Importable["interface.wx"]:
            raise libTewException("Unable to use wx")
        
        import wx.stc
        if not self.has_section("wxSTC"):
            raise ConfigurationError("wxSTC", msg="Section not found")
            
        if not hasattr(wx.stc, 'STC_LEX_{}'.format(self.get("wxSTC", "lexer_suffix").replace("'", ''))):
            raise libTewException("Sorry about that, but wx.stc does not support {} language yet".format(self.progname))

    def ConfigureWxWidget(self, widget):
        import wx.stc
        shortname = self["wxSTC"]["short_name"]
        keywords = []
        # Set Lexer
        widget.SetLexer(getattr(wx.stc, "STC_LEX_PYTHON"))
        # Set code keywords
        for option in self["keywords"]:
            keywords += self["keywords"][option].split('|')
        widget.SetKeyWords(0, " ".join(keywords))
        # widget.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "color goes here...")
        # Set highlight style
        widget.StyleClearAll()
        for option in self["highlight"]:
            widget.StyleSetSpec(getattr(wx.stc, "STC_{}_{}".format(shortname, option.upper()).replace("'", '')), self["highlight"][option])


