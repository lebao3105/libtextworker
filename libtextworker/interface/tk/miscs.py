from typing import Literal
from tkinter import Menu, Misc


def CreateMenu(
    items: list[tuple | dict[str]],
    parent: Misc | None = None,
    tearoff: Literal[0, 1] = 0,
    title: str = ...
) -> Menu:
    """
    Make a Tkinter menu with commands inside.
    
    Menu items list must follow the format below:

    ```python
    # Each menu item is made by a tuple
    (
     label[str], accelerator[str], handler[str|Callable],
     onvalue[=None], offvalue[=None], variable[=None],
     state["normal", "active", "disabled"][="normal"]
     kind["check", "option", "separator", "normal" or None][=None]
    )

    # Or a dict with the same parameters as the way above.
    # Recommended using dictionary since you can skip some values
    # without passing them None.
    ```

    @since 0.1.4 Added title parameter
    """

    target = Menu(parent, tearoff=tearoff, title=title)
    none_to_blank = {None: ""}
    none_to_blank_2 = {None: ...}

    def convert(item: str | None, type: Literal[1, 2]):
        if type == 2:
            return none_to_blank_2.get(item, item)
        else:
            return none_to_blank.get(item, item)

    for item in items:    
        if any(isinstance(item, tuple) for item in items):

            for label, acc, handler, onvalue, offvalue, variable, state, kind in item:
                label = convert(label, 1)
                acc = convert(acc, 1)
                handler = convert(handler, 2)
                onvalue = convert(onvalue, 2)
                offvalue = convert(offvalue, 2)
                variable = convert(variable, 2)
                state = "normal" if state is None else state
                kind = "normal" if state is None else kind
                break

        elif any(isinstance(item, dict) for item in items):

            label = convert(item.get("label", None), 1)
            acc = convert(item.get("accelerator", None), 1)
            handler = convert(item.get("handler", None), 2)
            onvalue = convert(item.get("onvalue", None), 2)
            offvalue = convert(item.get("offvalue", None), 2)
            variable = convert(item.get("variable", None), 2)
            state = item.get("state", "normal")
            kind = item.get("kind", "normal")

    args = {
        "accelerator": acc,
        "command": handler,
        "label": label,
        "state": state
    }

    if kind == "normal":
        target.add_command(**args)

    if kind == "check":
        target.add_checkbutton(
            **args, onvalue=onvalue, offvalue=offvalue, variable=variable
        )

    if kind == "separator": target.add_separator()

    if kind == "option":
        target.add_radiobutton(
            **args,
            variable=variable,
        )
        
    return target
