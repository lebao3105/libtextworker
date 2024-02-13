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

Look for the ```libtextworker.interface.base``` module first, then your toolkit support in ```libtextworker.interface```. Can you see your idea there?

Widgets inside ```libtextworker.interface.base``` are intended to help other people implementing the widget in their desired GUI as a skeleton, and therefore is recommended.

The ```WidgetBase``` class is used as a base for every other GUI classes here, has the following:

- \_\_init\_\_: Modify args and kwds to modify the parent option and take out the specific styles (w_styles keyword). Modify the "parent" option (specified by ```Parent_ArgName```) will lead to the actual widget to be placed in a frame/panel object (or whatever else), which is made as the Frame attribute. Returns the modified parementers.

- Parent_ArgName (attribute): What to describe this? Read the \_\_init\_\_ function above.

- Frame (attribute): See the \_\_init\_\_ function above.

- _Frame (attribute): It's the class for the Frame attribute. Whatever a class or a function, but don't put () after it, okay? You should be laughed at if you do that. For example this is not valid: ```_Frame = something() << that "()"```

- Styles (attribute): Widget's custom flags.

> WidgetBase.\_\_init\_\_ is perfect now, you don't need to overwrite it.

To make a new flags class: Import Flag, auto from ```enum``` module, create a Flag-derived \_FLAGS class, with auto() instances named \<widget_shortname>_<widget_option>.

If you want to create a skeleton, it's fine. Please check out our skeletons to see what you need to do (at least).

Create a new folder with your toolkit name (e.g pyqt5) in ```libtextworker.interface```. Don't forget to make \_\_init\_\_.py!

This is the skeleton for a GUI class:

```python
from enum import Flag, auto
from libtextworker.interface.base import WidgetBase
from <GUI> import <a fancy widget>, <frame>

# Jump straight to AWonderfulIdea class if you don't want
# to make any base classes

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

## What else?

Remember our flags? It's time to use them: all flags are stored in self.Styles, so just check if the desired flag is here:

```python
if AW_SOMETHING in self.Styles:
    # Do stuff...
```

Even the widget you make has its flags inherited from its parent too, you can make equaliment to them by making a dictionary[your_flags, toolkit_flags], make a new ```styles``` keyword (that is an ```enum.auto``` object) by checking if any of ```your_flags``` is in self.Styles.