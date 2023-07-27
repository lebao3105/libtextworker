import wx
import wx.adv

from typing import Any
from ...general import CraftItems
from .. import available_licenses
from ... import LICENSES

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

    SetArtists = infos.SetArtists
    SetCopyright = infos.SetCopyright
    SetDescription = infos.SetDescription
    SetDevelopers = infos.SetDevelopers
    SetDocWriters = infos.SetDocWriters
    SetIcon = infos.SetIcon
    SetName = infos.SetName
    SetTranslators = infos.SetTranslators
    SetVersion = infos.SetVersion
    SetWebSite = infos.SetWebSite

    def SetLicense(self, license: str, include_copyright: bool = False):
        """
        Set the long, multiline string containing the text of the program license.
        Not all license types are available. You can include your program copyright if needed.
        @see available_licenses
        @see SetCopyright
        """
        data = ""  # Our result
        if license in available_licenses:
            license = open(
                CraftItems(LICENSES, license + ".txt"),
                "r",
            ).read()
        if include_copyright == True and self.infos.GetCopyright() != "":
            data += self.infos.GetCopyright() + "\n"
        data += license
        self.infos.SetLicence(data)

    def ShowBox(self, event=None):
        """
        Shows a About dialog with infomations collected.
        @param event | None: wxPython event
        @return wx.adv.AboutBox: About window
        """
        return wx.adv.AboutBox(self.infos, self.Parent)
