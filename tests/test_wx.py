import wx
from libtextworker.interface.wx.about import AboutDialog
from libtextworker.interface.wx.editor import StyledTextControl

def test_wx():
    def aboutbox(evt):
        aboutdlg = AboutDialog()
        aboutdlg.SetName("libtextworker")
        aboutdlg.SetVersion("0.1.0")
        aboutdlg.SetDevelopers(["Le Bao Nguyen (@lebao3105)"])
        aboutdlg.SetWebSite("https://lebao3105.github.io/libtextworker")
        aboutdlg.SetLicense("GPL3_short")
        return aboutdlg.ShowBox()

    app = wx.App(0)
    fm = wx.Frame(None, title="libtextworker wxPython test")

    menubar = wx.MenuBar()
    the_only_one = wx.Menu()
    about = the_only_one.Append(wx.ID_ABOUT)

    fm.Bind(wx.EVT_MENU, aboutbox, about)

    menubar.Append(the_only_one, "The only one.")
    fm.SetMenuBar(menubar)

    StyledTextControl(fm)

    fm.Show()
    app.MainLoop()