"""
@package libtextworker.interface.tk.miscs
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

from typing import Literal
from tkinter import Menu, Misc

def CreateMenu(items: list[dict[str]], parent: Misc | None = None,
               tearoff: Literal[0, 1] = 0, title: str = "") -> Menu:
    """
    Make a Tkinter menu with commands inside.

    Available keys can be found on tkinter.Menu.add_*, but whatever:
    - label [str]           - handler [str|typing.Callable]
    - accelerator [str]     - onvalue [=None]
    - offvalue [=None]      - variable [=None]
    - state [normal, active, disabled][=normal]
    - kind [check, option, separator, normal] [=normal]

    @param items (list[dict[str]]): Menu items to be added
    @param parent (Misc | None = None): Where to place the Menu, optional
    @param tearoff (1 or 0, defaults to 0): Whatever... Optional, ofc
    @param title (str): Optional too, the title for the menu
    @return tkinter.Menu
    """

    target = Menu(parent, tearoff=tearoff, title=title)

    for item in items:
        label = item.get("label", "")
        acc = item.get("accelerator", "")

        handler = item.get("handler", "")
        onvalue = item.get("onvalue", "")
        offvalue =  item.get("offvalue", "")
        variable =  item.get("variable", "")

        state = item.get("state", "normal")
        kind = item.get("kind", "normal")

        args = {"accelerator": acc, "command": handler, "label": label, "state": state}

        if kind == "normal":
            target.add_command(**args)

        if kind == "check":
            target.add_checkbutton(**args, onvalue=onvalue, offvalue=offvalue, variable=variable)

        if kind == "separator":
            target.add_separator()

        if kind == "option": target.add_radiobutton(**args, variable=variable)

    return target
