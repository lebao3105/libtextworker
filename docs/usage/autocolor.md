# Auto color support for GUIs in libtextworker

Cuz why not!

libtextworker's auto color system is somewhat beautiful, although it's a little mess there.

Currently both Tk and wxPython are supported.

## Settings

It's defined under the "color" section in your theme file:
```ini
[color]
background = light
foreground = default
auto = yes
```

Nothing to explain here.

From version 0.1.4, I've added new configs called background-{variant} and foreground-{variant} as a part of the more dynamic color switch: custom colors for every mode.

### Color->Background

Type: string

Defaults to ```light```.

In 0.1.4, you can also use hex colors, or use custom colors defined in ```libtextworker.interface.colors``` (dictionary).

In 0.1.3, you only can choose between "dark" and "light".

### Color->Foreground

Type: string

Defaults to "default". That means the foreground color relies on the system scheme.

Options are many: "default", colors in ```libtextworker.interface.colors``` or ```libtextworker.interface._colors``` in 0.1.3. A hex color can be used.

### Color->auto

Type: boolean as a string/integer ("yes", "no", 0, 1, etc...)

Defaults to "yes" (enabled).

### Color->foreground/background-{variant}

> {variant} is either "dark" or "light"

Optional.

Type: string.

First debut: 0.1.4

No default value. Check for the foreground section above.

## Implementation for GUIs

Derive ```libtextworker.interface.manager.ColorManager```.

Functions to overwrite (not all of them):

* GetColor (or \_get\_color in older versions): get color defines
* GetFont (or \_get\_font in older versions): get font settings
* configure: configure (a) widget
* autocolor_run: you know it

Place your derived ColorManager class in libtextworker.interface.\<toolkit>/\_\_init\_\_.py.