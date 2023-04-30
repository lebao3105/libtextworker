import wx
import wx.adv

from typing import Any, final
from ...general import CraftItems, GetCurrentDir

## Available pre-stored licenses:
# * AGPL
# * GPL 3
# * LGPL 3
# * MIT
available_licenses = [
    "AGPL_full",
    "AGPL_short",
    "GPL3_full",
    "GPL3_short",
    "LGPL_3",
    "MIT",
]


@final
class AboutDialog:
    """
    About dialog built with wxPython.
    All self-set infomations are stored in the ```infos``` attribute.
    Just run ShowBox() to see your work.
    You can set the parent of the dialog if needed, use the Parent variable.
    This class is not sub-class-able.
    """

    infos = wx.adv.AboutDialogInfo()
    Parent: Any | None = None

    def SetArtists(self, artists):
        return self.infos.SetArtists(artists)

    def SetCopyright(self, text: str):
        return self.infos.SetCopyright(text)

    def SetDescription(self, des: str):
        return self.infos.SetDescription(des)

    def SetDevelopers(self, developers):
        return self.infos.SetDevelopers(developers)

    def SetDocWriters(self, writers):
        return self.infos.SetDocWriters(writers)

    def SetIcon(self, icon: wx.Icon):
        return self.infos.SetIcon(icon)

    def SetLicense(self, license: str, include_copyright: bool = False):
        """
        Set the long, multiline string containing the text of the program license.
        Not all license types are available. You can include your program copyright if needed.
        @version Updated on 0.1.3
        @see available_licenses
        @see SetCopyright
        """
        data = ""  # Our result
        if license in available_licenses:
            license = open(
                CraftItems(
                    GetCurrentDir(__file__), "../../licenses/{}.txt".format(license)
                ),
                "r",
            ).read()
        if include_copyright == True and self.infos.GetCopyright() != "":
            data += self.infos.GetCopyright() + "\n"
        data += license
        return self.infos.SetLicence(data)

    def SetName(self, name: str):
        return self.infos.SetName(name)

    def SetTranslators(self, translators):
        return self.infos.SetTranslators(translators)

    def SetVersion(self, version: str | float, longversion: str = ""):
        return self.infos.SetVersion(version.__str__(), longversion)

    def SetWebSite(self, address: str):
        return self.infos.SetWebSite(address)

    def ShowBox(self, event=None):
        """
        Shows a About dialog with infomations collected.
        @param event | None: wxPython event
        @return wx.adv.AboutBox: About window
        """
        return wx.adv.AboutBox(self.infos, self.Parent)
