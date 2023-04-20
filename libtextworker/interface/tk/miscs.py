from typing import Literal
from tkinter import Menu, Misc


def CreateMenu(
    items: list[tuple], parent: Misc | None = None, tearoff: Literal[0, 1] = 0
) -> Menu:
    """
    Make a Tkinter menu with commands.
    Menu items list must follow the format below:
    ```
    Each menu item is made under a tuple
    (
     label[str], accelerator[str], handler[str|Callable],
     onvalue[=None], offvalue[=None], variable[=None],
     state["normal", "active", "disabled"][="normal"]
     kind["check", "option", "separator", "normal" or None][=None]
    )
    ```
    """
    target = Menu(parent, tearoff=tearoff)
    none_to_blank = {None: ""}
    none_to_blank_2 = {None: ...}
    for item in items:
        for label, acc, handler, onvalue, offvalue, variable, state, kind in item:
            label = none_to_blank.get(label, label)
            acc = none_to_blank.get(acc, acc)

            onvalue = none_to_blank_2.get(onvalue, onvalue)
            offvalue = none_to_blank_2.get(offvalue, offvalue)
            variable = none_to_blank_2.get(variable, variable)

            if kind == None or "normal":
                target.add_command(
                    accelerator=acc, command=handler, label=label, state=state
                )
            if kind == "check":
                target.add_checkbutton(
                    accelerator=acc,
                    command=handler,
                    label=label,
                    offvalue=offvalue,
                    onvalue=onvalue,
                    state=state,
                    variable=variable,
                )
            if kind == "separator":
                target.add_separator()
            if kind == "option":
                target.add_radiobutton(
                    accelerator=acc,
                    command=handler,
                    label=label,
                    state=state,
                    variable=variable,
                )
    return target
