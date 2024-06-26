#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.
import os
import webbrowser
import wx
import wx.stc

from libtextworker.interface.base.dirctrl import DC_ONEROOT, DC_HIDEROOT

from . import HAS_ACOLOR, HASNT_ACOLOR, THEMEPATH, REPO_URL, API_URL, hasAutoColor
from libtextworker import __version__ as ver, general

general.test_import("wx")
from libtextworker.interface.wx import ColorManager
from libtextworker.interface.wx.about import AboutDialog
from libtextworker.interface.wx.actionrow import ActionRow
from libtextworker.interface.wx.editor import StyledTextControl
from libtextworker.interface.wx.miscs import CreateMenu

clrmgr = ColorManager(customfilepath=THEMEPATH)

def test_wx():
    """
    Events
    """

    # About dialog
    def aboutbox(evt):
        aboutdlg = AboutDialog()
        aboutdlg.SetName("libtextworker")
        aboutdlg.SetVersion(ver)
        aboutdlg.SetDevelopers(["Le Bao Nguyen (@lebao3105 on Github and Gitlab)"])
        aboutdlg.SetWebSite(REPO_URL)
        aboutdlg.SetLicense("GPL3_short")
        return aboutdlg.ShowBox()

    # Check for autocolor support
    def checkautocolor(evt):

        if not hasAutoColor():
            wx.MessageBox(HASNT_ACOLOR,
                          style=wx.ICON_ERROR | wx.OK | wx.CENTRE,
                          parent=fm)
        else:
            wx.MessageBox(HAS_ACOLOR,
                          style=wx.ICON_INFORMATION | wx.OK | wx.CENTRE,
                          parent=fm)

    """
    Full wxApp setup
    """

    app = wx.App(0)
    fm = wx.Frame(None, title="libtextworker wxPython demo")

    # Setup the menu bar
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
                None
            ),
            (wx.ID_ANY, "Check for auto-color support", None, checkautocolor, None)
        ],
    )

    menubar.Append(the_only_one, "The only one.")
    fm.SetMenuBar(menubar)

    # Notebook
    nb = wx.Notebook(fm)

    # Add a text editor
    te = StyledTextControl(nb)
    te.EditorInit()
    nb.AddPage(te, "StyledTextControl")

    # ActionRows
    pn = wx.Panel(nb)
    sz = wx.BoxSizer(wx.VERTICAL)
    pn.SetSizer(sz)
    nb.AddPage(pn, "ActionRows", select=True)

    for i in range(0, 5):
        _lol = ActionRow()
        _lol.SetParent(pn)
        _lol.PlaceObj(wx.StaticText, label=f"testtesttest{str(i)}")

        if 0 <= i <= 2:
            _lol.PlaceObj(wx.CheckBox, style=wx.CHB_DEFAULT | wx.ALIGN_RIGHT)
        else:
            _lol.PlaceObj(wx.Button, style=wx.ALIGN_RIGHT)

        sz.Add(_lol, 0, wx.ALL | wx.EXPAND, 5)

    # Dir*
    from libtextworker.interface.wx.dirctrl import EVT_FILE_CREATED, EVT_FILE_CLOSED, EVT_FILE_DELETED, DirCtrl
    dirctrl = DirCtrl(nb, w_styles=DC_HIDEROOT)
    dirctrl2 = DirCtrl(nb, w_styles=DC_ONEROOT)

    dirctrl.SetFolder("./po")
    dirctrl.SetFolder("./tests")

    dirctrl2.SetFolder(os.path.expanduser("./libtextworker"))
    def ref(evt, path, ctrl):
        wx.LogMessage(f"{evt} file {path}")  
        ctrl.Refresh()

    for ctrl in [dirctrl, dirctrl2]:
        ctrl.Bind(EVT_FILE_CREATED, lambda evt: ref("Created", evt.path, ctrl))
        ctrl.Bind(EVT_FILE_CLOSED, lambda evt: ref("Closed", evt.path, ctrl))
        ctrl.Bind(EVT_FILE_DELETED, lambda evt: ref("Deleted", evt.path, ctrl))
        # I'm too lazy to add more

    nb.AddPage(dirctrl, "DirCtrl (multiple root nodes)")
    nb.AddPage(dirctrl2, "DirCtrl (one root node)")

    # Log
    log = wx.TextCtrl(nb, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL)
    nb.AddPage(log, "Logs")

    clrmgr.configure(nb, childs_too=True)
    clrmgr.autocolor_run(nb)

    wx.Log.SetActiveTarget(wx.LogTextCtrl(log))
    fm.Show()
    app.MainLoop()
