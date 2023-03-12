import wx
from libtextworker.interface.wx.editor import StyledTextControl

def test_ui():
    app = wx.App(0)
    fm = wx.Frame(None)

    StyledTextControl(parent=fm, id=wx.ID_ANY, line_number=True)

    fm.Show()
    app.MainLoop()