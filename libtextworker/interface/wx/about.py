import wx
import wx.adv

from typing import Any, final
from libtextworker.general import CraftItems, libTewException, GetCurrentDir

available_licenses = ["GPL3_short", "GPL3_full", "MIT"]


@final
class AboutDialog:
    """
    About dialog built with wxPython.
    All self-set infomations are stored in the ```infos``` attribute. Just run ShowBox().
    You can set the parent of the dialog if needed, use the Parent variable.
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

    def SetLicense(self, license: str):
        """
        Set the long, multiline string containing the text of the program license.
        Not all license types are available. Please see the attribute available_licenses (not in this class but in the same module).
        """
        if license not in available_licenses:
            raise libTewException(
                "Sorry about this, but we couldn't find any license as requested ({}). You should notify this for libtextworker devs".format(
                    license
                )
            )
        targetfile = CraftItems(
            GetCurrentDir(__file__), "../../licenses/{}.txt".format(license)
        )
        data = open(targetfile, "r").read()
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
