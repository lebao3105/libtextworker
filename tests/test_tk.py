import tkinter as tk
import tkinter.ttk as ttk

from libtextworker import _importer
_importer.test_import("tkinter")
from libtextworker.interface.tk import ColorManager
from libtextworker.interface.tk.editor import StyledTextControl

clrmgr = ColorManager()


def test_tk():
    app = tk.Tk()
    app.geometry("300x258")
    fm = ttk.Frame(app)

    ttk.Label(fm, text="Hello world!").pack()
    ttk.Button(fm, text="This is a button").pack()
    ttk.Checkbutton(fm, text="A checkbutton").pack()

    nb = ttk.Notebook(fm)
    
    pb = ttk.Progressbar(nb, phase=8, value=0.0)
    pb.start()

    te = StyledTextControl(nb)
    te.EditorInit()

    nb.add(ttk.Combobox(nb, values=["one", "two", "three"]), text="Tab 1")
    nb.add(pb, text="Tab 2")
    nb.add(te, text="Tab 3")

    clrmgr.configure(fm, True)
    clrmgr.configure(nb, True)
    nb.pack(expand=True, fill="both")
    fm.pack(expand=True, fill="both")

    app.mainloop()
