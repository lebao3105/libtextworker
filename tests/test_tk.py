# 	A cross-platform library for Python apps.
# 	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
# 	This is a part of the libtextworker project.
# 	Licensed under the GNU General Public License version 3.0 or later.

import os
import platform
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mgb

from . import THEMEPATH, GITHUB_URL
from libtextworker import __version__ as libver, general

general.test_import("tkinter")
from libtextworker.interface.tk import ColorManager
from libtextworker.interface.tk.about import AboutDialog
from libtextworker.interface.tk.dirctrl import *
from libtextworker.interface.tk.editor import StyledTextControl
from libtextworker.interface.tk.findreplace import FindReplace

clrmgr = ColorManager(customfilepath=THEMEPATH)


def test_tk():
    app = tk.Tk()
    app.geometry("300x258")

    fm = ttk.Frame(app)

    # About dialog
    aboutdlg = AboutDialog()
    aboutdlg.SetProjectName("libtextworker")
    aboutdlg.SetProjectVersion(libver)
    aboutdlg.SetProjectDescription("A Python library made for GUI apps.")
    aboutdlg.SetProjectSite(GITHUB_URL)
    aboutdlg.SetAppTesters(["Le Bao Nguyen"])
    aboutdlg.SetDevelopers(["Le bao Nguyen"])
    aboutdlg.SetProjectLicense("GNU General Public License Version 3")

    if platform.system() == "Darwin":
        app.createcommand("tkAboutDialog", lambda: aboutdlg.ShowDialog(fm))

    # Build the UI
    ttk.Label(fm, text="Hello world!").pack()
    ttk.Button(
        fm, text="Click it!", command=lambda: (aboutdlg.ShowDialog(fm))
    ).pack()
    ttk.Checkbutton(fm, text="A checkbutton").pack()

    nb = ttk.Notebook(fm)

    dc = DirCtrl(nb, show="tree")
    dc.SetFolder(os.path.expanduser("~/Desktop"))
    ## Some of file system events are bond here.
    ## Why not more? I'm lazy.
    ## Better with a status bar
    dc.bind(FileCreatedEvent, lambda evt: mgb.showinfo("New created file", f"Created {evt.path}"))
    dc.bind(FileDeletedEvent, lambda evt: mgb.showinfo("New deleted file", f"Deleted {evt.path}"))
    dc.bind(FileEditedEvent, lambda evt: mgb.showinfo("New edited file", f"Edited {evt.path}"))
    dc.bind(FileOpenedEvent, lambda evt: mgb.showinfo("File opened", f"Opened {evt.path}"))
    dc.Frame.pack(expand=True, fill="both")

    te = StyledTextControl(nb)
    te.EditorInit()
    FindReplace(fm, te).mainloop()
    te.pack(expand=True, fill="both")

    nb.add(ttk.Combobox(nb, values=["one", "two", "three"]), text="Tab 1")
    nb.add(dc.Frame, text="Tab 2")
    nb.add(te._frame, text="Tab 3")

    clrmgr.configure(fm, childs_too=True)
    clrmgr.configure(nb, childs_too=True)
    nb.pack(expand=True, fill="both")
    fm.pack(expand=True, fill="both")

    app.mainloop()
