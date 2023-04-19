import tkinter as tk
import tkinter.ttk as ttk

from libtextworker.interface.tk import clrmgr


def test_tk():
    app = tk.Tk()
    app.geometry("300x258")
    fm = ttk.Frame(app)
    label = ttk.Label(fm, text="Hello world!")
    button = ttk.Button(fm, text="No event binded")

    clrmgr.configure(fm, True)

    label.pack()
    button.pack()
    fm.pack()

    app.mainloop()
