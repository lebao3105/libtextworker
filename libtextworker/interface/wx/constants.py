"""
@package libtextworker.interface.wx.constants
@brief Constants for wxPython.
"""
import wx

# Font weight
FONTWT = {
    "light": wx.FONTWEIGHT_LIGHT,
    "normal": wx.FONTWEIGHT_NORMAL,
    "semibold": wx.FONTWEIGHT_SEMIBOLD,
    "bold": wx.FONTWEIGHT_BOLD,
    "maxlight": wx.FONTWEIGHT_EXTRALIGHT,
    "maxbold": wx.FONTWEIGHT_EXTRABOLD,
}

# Font style
FONTST = {"normal": wx.FONTSTYLE_NORMAL, "italic": wx.FONTSTYLE_ITALIC}

# Font size
FONTSZ = {
    "normal": 12,
    "small": 8,
    "large": 16,
}

# Logging functions
LOG_CRITICAL = wx.LogFatalError
LOG_DEBUG = wx.LogDebug
LOG_ERROR = wx.LogError
LOG_EXCEPTION = wx.LogError
LOG_NORMAL = wx.LogMessage
LOG_WARNING = wx.LogWarning
