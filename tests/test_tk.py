import tkinter as tk
import tkinter.ttk as ttk

from . import THEMEPATH
from libtextworker import _importer, __version__ as libver
_importer.test_import("tkinter")
from libtextworker.interface.tk import ColorManager
from libtextworker.interface.tk.about import AboutDialog
from libtextworker.interface.tk.editor import StyledTextControl

clrmgr = ColorManager(customfilepath=THEMEPATH)


def test_tk():
    app = tk.Tk()
    app.geometry("300x258")
    
    fm = ttk.Frame(app)
    aboutdlg = AboutDialog()
    aboutdlg.SetProjectName("libtextworker")
    aboutdlg.SetProjectVersion(libver)
    aboutdlg.SetProjectDescription("A Python library made for GUI apps.")
    aboutdlg.SetAppTesters(["Le Bao Nguyen"])
    aboutdlg.SetDevelopers(["Le bao Nguyen"])
    aboutdlg.SetProjectLicense("GPL3_full")

    ttk.Label(fm, text="Hello world!").pack()
    ttk.Button(fm, text="Try to click it;)!", command=lambda :(aboutdlg.ShowDialog(fm))).pack()
    ttk.Checkbutton(fm, text="A checkbutton").pack()

    nb = ttk.Notebook(fm)
    
    pb = ttk.Progressbar(nb, phase=8, value=0.0)
    pb.start()

    te = StyledTextControl(nb)
    te.EditorInit(custom_theme_path=THEMEPATH)
    te.pack(expand=True, fill="both")

    nb.add(ttk.Combobox(nb, values=["one", "two", "three"]), text="Tab 1")
    nb.add(pb, text="Tab 2")
    nb.add(te._frame, text="Tab 3")

    clrmgr.configure(fm, True)
    clrmgr.configure(nb, True)
    nb.pack(expand=True, fill="both")
    fm.pack(expand=True, fill="both")

    app.mainloop()