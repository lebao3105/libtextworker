"""Default UI settings"""
stock_ui_configs = {
    "color": {
        "background": "light",
        "foreground": "default",
        "auto": "yes"
        # New in 0.1.4:
        # background and foreground color specificially for light and dark mode,
        # suffixed by "-light" and/or "-dark"
        # by default we won't leave it here, this is for the end-users
    },
    "font": {  # default value 'normal' now switched to 'system'
        "style": "system",
        "weight": "system",
        "family": "system",
        "size": "system",
    },
}

"""Default editor configs"""
stock_editor_configs = {
    "indentation": {"size": 4, "type": "tabs", "show_guide": "yes"},
    "menu": {"enabled": "yes"},
    "editor": {"line_count": "yes", "dnd_enabled": "yes", "wordwrap": "yes"},
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
    "light_green": "#20eaaa",
}

## Available pre-stored licenses
available_licenses = [
    "AGPL_full",
    "AGPL_short",
    "GPL3_full",
    "GPL3_short",
    "LGPL_3",
    "MIT",
]
