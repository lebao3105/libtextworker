# Auto color support for GUIs in libtextworker

Cuz why not!

libtextworker's auto color system is somewhat beautiful, although it's a little mess there.

Currently both Tkinter and wxPython are supported.

But take a note about this: not all GUI widgets can be themed well, as they may use API that does not allow customizations well, or because of the toolkit support from libtextworker. Widgets may be half-themed, or not themed at all.

As always I (the only developer here) welcome patches.

## Settings

It's defined under the "color" section in your theme file, like this:

```ini
[color]
background = light
foreground = default
auto = yes
```

Starting from version 0.1.4, you can use hex colors and RGB colors (only from the non-development release).

There are some named colors, look at ```libtextworker.interface.colors``` or ```libtextworker.interface._colors``` in 0.1.3.

### color->background

Type: string

Defaults to ```light```.

On previous versions, you only can choose between "dark" and "light".

### color->foreground

Type: string

Defaults to "default". That means the foreground color relies on the system scheme.

Options are many: "default", colors in ```libtextworker.interface.colors``` or ```libtextworker.interface._colors``` in 0.1.3.

### color->auto

Type: boolean as a string/integer ("yes", "no", 0, 1, etc... look at `GetConfig.yes_values` and `GetConfig.no_values`)

Defaults to "yes" (enabled).

### color->foreground/background-{variant}

> `{variant}` is either "dark" or "light"

Optional.

Type: string.

First debut: 0.1.4

No default value. Check for options above.

### highlight->background{,-{mouse,finder}}

Highlight colors. For text highlighted by mouse or a Find/Replace dialog.

Optional.

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

See ColorManager's `set*func` (`*` = wildcard):

* `setcolorfunc`: Background
* `setfontcfunc`: Foreground (or font color/fontc in function name, no typo here!)
* `setfontandcolorfunc`: The combination of the 2 functions above (available on 0.1.4+)

Pass your widget/widget class, the function you want to use, and parameters if any (tuple type seems not working, don't know why?).

`ColorManager.configure` will handle this itself.