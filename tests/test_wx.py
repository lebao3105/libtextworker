import webbrowser
import wx
from libtextworker import __version__ as ver
from libtextworker import _importer
_importer.test_import("wx")
from libtextworker.interface.wx.about import AboutDialog
from libtextworker.interface.wx.editor import StyledTextControl
from libtextworker.interface.wx.miscs import CreateMenu

GITHUB_URL = "https://github.com/lebao3105/libtextworker"
API_URL = "https://lebao3105.github.io/libtextworker"


def test_wx():
    def aboutbox(evt):
        aboutdlg = AboutDialog()
        aboutdlg.SetName("libtextworker")
        aboutdlg.SetVersion(ver)
        aboutdlg.SetDevelopers(["Le Bao Nguyen (@lebao3105)"])
        aboutdlg.SetWebSite(GITHUB_URL)
        aboutdlg.SetLicense("GPL3_short")
        return aboutdlg.ShowBox()

    app = wx.App(0)
    fm = wx.Frame(None, title="libtextworker wxPython test")

    menubar = wx.MenuBar()
    the_only_one = CreateMenu(
        fm,
        [
            (wx.ID_ABOUT, "About", "About this test", aboutbox, None),
            (
                wx.ID_HELP_CONTENTS,
                "API Documents",
                None,
                lambda evt: webbrowser.open(API_URL),
                None,
            ),
        ],
    )

    menubar.Append(the_only_one, "The only one.")
    fm.SetMenuBar(menubar)

    StyledTextControl(fm).EditorInit()

    fm.Show()
    app.MainLoop()
