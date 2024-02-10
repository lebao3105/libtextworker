"""
@package libtextworker.interface.tk.constants
@brief Constants for Tkinter.
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

from tkinter.messagebox import showerror, showinfo, showwarning
from ...import _

__all__ = ["LOG_EXCEPTION", "LOG_CRITICAL", "LOG_DEBUG", "LOG_NORMAL", "LOG_WARNING", "LOG_ERROR"]

# These "logging" functions are not actually do logging yet.
# LOG_CRITICAL: Probably I'd like to... exit with code -1.
# On wxPython, LOG_CRITICAL uses code 3 (C runtime abort function I guess)
LOG_EXCEPTION = LOG_ERROR = lambda message: showerror(_("An error occured"), message)
LOG_CRITICAL = lambda message: (showerror(_("A critical error occured!"), message), exit(-1))
LOG_DEBUG = lambda message: showinfo(_("Debug message"), message)
LOG_NORMAL = lambda message: showinfo(_("Infomation (used for logging)"), message)
LOG_WARNING = lambda message: showwarning(_("Warning"), message)