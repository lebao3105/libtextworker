# Auto color support for GUIs in libtextworker

Cuz why not!

libtextworker's auto color system is somewhat beautiful, although it's a little mess there.

Currently both Tk and wxPython are supported.

## Settings

It's defined under the "color" section in your theme file, like this:

```ini
[color]
background = light
foreground = default
auto = yes
```

### Color->Background

Type: string

Defaults to ```light```.

Since 0.1.4, you can also use hex colors, or use custom colors defined in ```libtextworker.interface.colors``` (dictionary).

On previous versions, you only can choose between "dark" and "light".

### Color->Foreground

Type: string

Defaults to "default". That means the foreground color relies on the system scheme.

Options are many: "default", colors in ```libtextworker.interface.colors``` or ```libtextworker.interface._colors``` in 0.1.3. A hex color can be used.

### Color->auto

Type: boolean as a string/integer ("yes", "no", 0, 1, etc...)

Defaults to "yes" (enabled).

### Color->foreground/background-{variant}

> `{variant}` is either "dark" or "light"

Optional.

Type: string.

First debut: 0.1.4

No default value. Check for options above.

## Implementation for GUIs

The main class is ```libtextworker.interface.manager.ColorManager```.

Functions to overwrite (not all of them):

* GetColor (or \_get\_color in older versions): get color defines
* GetFont (or \_get\_font in older versions): get font settings
* configure: configure (a) widget

Place your derived ColorManager class in libtextworker.interface.\<toolkit>/\_\_init\_\_.py.

New in `0.1.4`: `UISync` class. As the name says, this class uses `darkdetect.listener` to change the application color when needed.

You probably don't need to derive this, as this is made for all toolkits. You even can use any function you want, not only `ColorManager.configure`.

Probably `ColorManager.configure` is preferred.

Run `ColorManager.autocolor_run(object)` to get started.

## Custom functions for coloring

See ColorManager's set*func:

* `setcolorfunc`: Background
* `setfontcfunc`: Foreground (or font color/fontc in function name, no typo here!)
* `setfontandcolorfunc`: The combination of the 2 functions above (available on 0.1.4+)

Pass your widget/widget class, the function you want to use, and parameters if any (tuple type seems not working, don't know why?).

`ColorManager.configure` will handle this itself.