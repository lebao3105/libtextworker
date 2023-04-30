import tkinter as tk
import tkinter.ttk as ttk

from libtextworker.interface.tk import ColorManager

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
    nb.add(ttk.Combobox(nb, values=["one", "two", "three"]), text="Tab 1")
    nb.add(pb, text="Tab 2")
    nb.pack(expand=True, fill="both")
    pb.start()

    clrmgr.configure(fm, True)
    fm.pack()

    app.mainloop()
