# Implement a new GUI support for libtextworker

So you want to make your own widgets, eh?

You can look at this guide!

## Ideas

There are plenty of ideas:

* Directory tree
* Editable list
* etc...

The percentage of a successful widget depends on the writer's skill, and the power of the target toolkit.

Normally a GUI support in libtextworker has:

* Color scheme, including auto color
* Widgets

## Startup

First, look for ```libtextworker.interface.base```. It may have the base class for the type of widget you want to make. You may also see classes with "_FLAGS" suffix, they contain flags for a specific object.

If you see your widget type in the base module, derive it + suitable GUI object and start making your own. See the code below for more. If not, create one. Also a flags class if needed. Must be made under a module in ```libtextworker.interface.base```.

To make a new flags class: Import Flag, auto from ```enum``` module, create a Flag-derived _FLAGS class, with auto() instances named \<widget_shortname>_<widget_option>.

Create a new folder with your toolkit name (e.g pyqt5) in ```libtextworker.interface```. Don't forget to make \__init__.py!

This is the skeleton for a GUI class:

```python
from enum import Flag, auto
from libtextworker.interface.base import WidgetBase
from <GUI> import <a fancy widget>, <frame>

class AW_FLAGS(Flag):
    AW_FLAGONE = auto()
    AW_FLAGTWO = auto()
    ...

class AWonderfulThing(WidgetBase):

    Styles = AW_FLAGONE | AW_FLAGTWO

    def Foo(this, event):
        ...

# Put this in a module under libtextworker.interface.<GUI>
class AWonderfulIdea(<a fancy widget>, WidgetBase):

    _Frame = <frame>

    def __init__(this, *args, **kwds):
        args, kwds = WidgetBase.__init__(this, *args, **kwds)
        <a fancy widget>.__init__(this, *args, **kwds)
        # Do something more

    def Foo(this, event):
        """
        A function which is called when an event occurs.
        """
```

## How it works

In the code above, ```AW_FLAGS``` is an enum.Flag-derived class with ```AW_FLAG*``` variable as the flags for "AWonderfulIdea" widget.

AWonderfulThing: The base skeleton for a widget. Default styles and actions. Don't need to derive WidgetBase.\__init__.

AWonderfulIdea: Derived from a GUI object and WidgetBase, when called it will ask WidgetBase to put itself in a frame, class defined by _Frame property. WidgetBase.\__init__ gets ``args`` and ``kwds``, get styles passed by the "w_styles" kwds keyword (default is the Styles attribute), put the widget in a frame (if appalicable), remove the parent widget option from args/kwds, and return modified items.