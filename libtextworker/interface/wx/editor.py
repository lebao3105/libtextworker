import wx.stc
from ..manager import ColorManager

class StyledTextControl(wx.stc.StyledTextCtrl):

    def __init__(self, id=wx.ID_ANY, line_number:bool = False, **kw):
        kw["style"] = kw.get("style", 0) | wx.stc.STC_STYLE_DEFAULT
        super().__init__(id=id, **kw)

        clrmgr = ColorManager()

        self.EnableLineCount(line_number)
        # self.AddText("import wx\nprint('hello')")

        # Base editor color
        bg, fg = clrmgr._get_color()
        bg = "#" + "%02x%02x%02x" % bg
        fg = "#" + "%02x%02x%02x" % fg
        self.StyleSetSpec(0, "fore:{},back:{}".format(fg, bg))
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, "fore:{},back:{}".format(fg, bg))

        # Setup a margin to hold fold markers
        self.SetMarginType(2, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, wx.stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)

        # and now set up the fold markers
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEREND, wx.stc.STC_MARK_BOXPLUSCONNECTED, fg, bg)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.stc.STC_MARK_BOXMINUSCONNECTED, fg, bg)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERMIDTAIL, wx.stc.STC_MARK_TCORNER, fg, bg)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERTAIL, wx.stc.STC_MARK_LCORNER, fg, bg)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERSUB, wx.stc.STC_MARK_VLINE, fg, bg)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDER, wx.stc.STC_MARK_BOXPLUS, fg, bg)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPEN, wx.stc.STC_MARK_BOXMINUS, fg, bg)

        # hlt = LanguageHighlight()
        # hlt.LanguageInit(self.Value)
        # hlt.InitializeUIType()
        # hlt.ConfigureWxWidget(self)

        # TODO: Fix dark mode
        clrmgr.setcolorfunc(
            "textw", self.StyleSetBackground, wx.stc.STC_STYLE_DEFAULT
        )
        clrmgr.setfontcfunc(
            "textw", self.StyleSetForeground, wx.stc.STC_STYLE_DEFAULT
        )
        clrmgr.configure(self)

        self.Bind(wx.stc.EVT_STC_MODIFIED, self.OnSTCModify)
    
    def OnSTCModify(self, event):
        if event:
            pos = event.GetPosition()
            length = event.GetLength()
        else:
            pos = 0
            length = self.GetLength()
        self.StartStyling(pos)
        self.SetStyling(length, 0)
        event.Skip()
    
    def EnableLineCount(self, set:bool):
        if set == True:
            self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
            self.SetMarginMask(1, 0)
            self.SetMarginWidth(1, 40)
        else:
            self.SetMarginWidth(1, 0)
        

