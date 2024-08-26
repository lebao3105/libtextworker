# 	A cross-platform library for Python apps.
# 	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
# 	This is a part of the libtextworker project.
# 	Licensed under the GNU General Public License version 3.0 or later.

import os
import platform
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mgb
import webbrowser


from . import API_URL, HAS_ACOLOR, HASNT_ACOLOR, THEMEPATH, REPO_URL, hasAutoColor
from libtextworker import __version__ as libver, general

general.test_import("tkinter")
from libtextworker.interface import stock_ui_configs
from libtextworker.interface.tk import ColorManager
from libtextworker.interface.tk.about import AboutDialog
from libtextworker.interface.tk.dirctrl import *
from libtextworker.interface.tk.editor import StyledTextControl
from libtextworker.interface.tk.findreplace import FindReplace
from libtextworker.interface.tk.miscs import CreateMenu

clrmgr = ColorManager(stock_ui_configs, THEMEPATH)


def test_tk():
    app = tk.Tk()
    app.geometry("300x258")

    fm = ttk.Frame(app)

    # About dialog
    aboutdlg = AboutDialog()
    aboutdlg.SetProjectName("libtextworker")
    aboutdlg.SetProjectVersion(libver)
    aboutdlg.SetProjectDescription("A Python library made for GUI apps.")
    aboutdlg.SetProjectSite(REPO_URL)
    aboutdlg.SetAppTesters(["Le Bao Nguyen"])
    aboutdlg.SetDevelopers(["Le bao Nguyen"])
    aboutdlg.SetProjectLicense(
        open(os.path.join(general.GetCurrentDir(__file__), "../LICENSE")).read()
    )
    
    def showaboutdialog():
        clrmgr.configure(aboutdlg.ShowDialog(fm), childs_too=True)

    # Build menu bar
    menubar = tk.Menu(app)
    menubar.add_cascade(
        label="The only one",
        menu=CreateMenu(
            [
                {
                    'label': 'API Documents',
                    'handler': lambda evt: webbrowser.open(API_URL)
                },
                {
                    'label': 'Check for auto coloring support',
                    'handler': lambda evt: mgb.showinfo(message=HAS_ACOLOR if hasAutoColor() else HASNT_ACOLOR)
                }
            ],
            fm
        )
    )
    app.config(menu=menubar)

    # Build the UI
    ttk.Label(fm, text="Hello world!").pack()
    ttk.Button(fm, text="About this project", command=showaboutdialog).pack()
    ttk.Checkbutton(fm, text="A checkbutton").pack()

    nb = ttk.Notebook(fm)

    ## Directory control
    dc = DirCtrl(nb, show="tree", refresh_on_changes=True)
    dc.SetFolder(os.path.expanduser("~/Desktop"))

    for event in ["Edited", "Created", "Deleted", "Opened", "Closed", "Moved"]:
        dc.bind(f"<<File{event}>>",
                lambda evt: mgb.showinfo("Information", f"event {evt.data}"))

        if event not in ["Opened", "Closed"]:
            dc.bind(f"<<Dir{event}>>",
                    lambda evt: mgb.showinfo("Information", f"event {evt.data}"))

    dc.Frame.pack(expand=True, fill="both")

    ## Text editor
    te = StyledTextControl(nb)
    te.EditorInit()
    te.pack(expand=True, fill="both")

    def openfrDialog():
        dlg = tk.Toplevel(fm)
        FindReplace(dlg, te, TK_USEPACK, True).pack(expand=True, fill="both")
        clrmgr.configure(dlg, childs_too=True)

    te.addMenucmd(command=openfrDialog, label="Find & Replace")

    # Now add tabs into the notebook and color the entire applicaiton
    nb.add(ttk.Combobox(nb, values=["one", "two", "three"]), text="Tab 1")
    nb.add(dc.Frame, text="Tab 2")
    nb.add(te._frame, text="Tab 3")

    clrmgr.configure(fm, childs_too=True)
    clrmgr.configure(nb, childs_too=True)

    nb.pack(expand=True, fill="both")
    fm.pack(expand=True, fill="both")

    app.mainloop()
