"""
@package libtextworker.interface
@brief GUI widgets and functions from libtextworker.
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

"""
Default UI settings
"""
stock_ui_configs = {
    "color": {
        "background": "light",
        "foreground": "default",
        "auto": "yes"
        # New in 0.1.4:
        # background and foreground color specificially for light and dark mode,
        # suffixed by "-light" and/or "-dark"
        # by default we won't leave it here
    },
    "font": {  # default value 'normal' now switched to 'system'
        "style": "system",
        "weight": "system",
        "family": "system",
        "size": "system",
    },
    "highlight": {
        # Also new in this version: highlighted background and foreground,
        # for hightlight by mouse and by finder.
        # Key for each situations would use "-mouse" and "-finder" prefixes.
        "background": "",
        "foreground": ""
    }
}

"""
Default editor configs
"""
stock_editor_configs = {
    "indentation": {
        "size": 4,
        "type": "tabs",
        "show_guide": "yes",
        "backspace_unindents": "yes",
    },
    "menu": {"enabled": "yes"},
    "editor": {
        "line_count": "yes",
        "dnd_enabled": "yes",
        "wordwrap": "yes",
        "view_whitespaces": "yes",
        "viewEOL": "no",
    },
}

"""
Custom colors.
@since 0.1.3 first debut on libtextworker.interface._colors
@since 0.1.4 moved to libtextworker.interface
"""
colors = {
    "light": "#ffffff",
    "dark": "#0f0e0d",
    "green": "#00ff00",
    "red": "#ff0000",
    "rose": "#ffaa95",
    "light_pink": "#ffd1d6",
    "light_green": "#95ffaa",
    "black": "#000000"
}

from libtextworker.general import test_import
test_import("darkdetect")