# Choose the right toolkit you want

libtextworker supports 2 GUI toolkits: Tkinter and wxPython. [Tkinter][TkinterSite] is the Python bindings of [Tcl/Tk][TclSite], and [wxPython][wxPy] is the Python version of [wxWidgets][wxSite] - an universal solution for cross-platform GUI apps without being different from the current OS's look.

Both 2 platforms are powerful, one factor for this is how you use it.

## Comparison

| Toolkit  | Installation                                                             | The core                  | Best for...                                    | Limitations                                             |
|----------|--------------------------------------------------------------------------|---------------------------|------------------------------------------------|---------------------------------------------------------|
| Tkinter  | Not from Pypi      | Tk toolkit                | Python GUI newbies/who want a simple/good interface with themes | Ugly on Linux, some goods are not here yet              |
| wxPython | Get from Pypi | Win32 API, Cocoa, Gtk, Qt | People who want a more powerful application    | Takes time to install + learn |

Notes:

* About Tk(inter)'s ugly UI: many people hate it - you can search the internet about it, and I don't know how to explain how and why. Fortunately, you can get many modern themes around GitHub! Even a workaround for the native Gtk look for Tkinter/Tk has been started years ago. Only one word before we continue: use Tkinter.ttk as much as possible, because ttk widgets are "colored" - better than the default Tkinter one.

* About wxPython installation: if Pypi can't find a wheel (it's something like .msi or .deb) for your machine, it will start building one. This is a normal behaviour, but you have to look for the dependencies wxPython needs.

* About Tkinter installation: on Windows there's an option in the installer (not MS Store one?). On *NIX, Tkinter is separated from the main Python package.

## What about libtextworker?

For Tkinter support: it's here as the ```libtextworker.interface.tk``` package.

For wxPython, it's ```libtextworker.interface.wx```.

The support is not really equal for both GUIs.

[TclSite]: https://tcl.tk
[TkinterSite]: https://docs.python.org/3/library/tk.html
[wxPy]: https://wxpython.org
[wxSite]: https://wxwidgets.org

<div class="section_buttons">

| Previous                   |                       Next |
|:---------------------------|---------------------------:|
| [What to pick?](gettheright.md)                  | [Hello world!](firstcode.md) |

</div>