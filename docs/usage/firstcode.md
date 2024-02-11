# First steps

## What version of libtextworker I want?

```python
# Assuming this is your __init__.py/main file
# Because the code below should be called first
# before any other libtextworker calls
from libtextworker.versioning import require
require("libtextworker", "0.1.3")
```

In the code above, we import the require function from the libtextworker.versioning module, then use it to "require" version 0.1.3 of libtextworker. This ensures that your project is using the library with version 0.1.3, nothing else.

Here's the ```require``` function parameters:

```python
def require(
        project         : str,
        target_version  : str
):
        """
        Ensures that a project is available for the requested version OR HIGHER.
        @param project (str): Project name
        @param target_version (str): Project version you want to have
        """
```

You can use this function for other packages, just make sure that the package has ```__version__``` attribute.

There are many functions for your use: `require_exact`, `require_lower`, and even `is_development_version`, `is_development_version_from_project` for verions type-checking.

## Explore variables

The top-level module has some useful attributes:

* THEMES_DIR (str): Defaults to ```~/.configs/textworker/themes```; where all themes for GUIs are placed
* EDITOR_DIR (str): Defauls to ```~/.configs/textworker/editorconfigs/```; default configs directory for GUI editors
* Importable (dict): An alias to ```general.Importable```, contains check results for Python modules.

In libtextworker.general module we have a variable called available_toolkits (since 0.1.3), indicates supported GUI toolkits. Only wxPython and Tkinter are supported. Also we have LOG_PATH shows us where the log file is located, TOPLV_DIR for the top-level settings path.

## Choose what you want

Take a look at all library modules:

* ```general```: Has functions that mostly about file/directory touch. They are born to make file operations easier.
* ```get_config``` ported from texteditor, contains GetConfig class which is an advanced INI parser (json import/export ongoing), with backup, value aliases, and runtime update.
* ```versioning```: See above.
* ```interface.manager```: Contains ColorManager which handles GUI widgets color/font
* ```interface._colors``` (since 0.1.3) specifies *some* colors. Moved to ```interface``` since version 0.1.4.
* subfolders in ```interface```: GUIs support ('wx' for wxPython, 'tk' for Tkinter)

## Packaging

Head over to this [page](packaging.md).

## Bonus: A basic example about using libtextworker GUI work (skeleton base for all supported toolkits)

```python
from libtextworker.general import test_import
from libtextworker.interface.available_toolkit import ColorManager
from libtextworker.interface.available_toolkit.miscs import CreateMenu
# Here we use App, Button, CheckButton, Frame classes
from your_preferred_gui import App, Button, CheckButton, Frame

if not test_import("your_tookit_here"):
    ... # Check if you can use your preferred tookit here

app = App()
mainFrame = Frame(parent=None, title="libtextworker example")

# Create a menu bar with menus inside. This will vary on different GUIs.
menuBar = mainFrame.CreateMenuBar()
menu1 = CreateMenu(mainFrame,
        [
                # Menu item syntax:
                # Label - handler - accelerator - type - isDisabled
                ("Hello world", lambda evt: print("hello!"), None, None, None),
                ...
        ]
)
menuBar.Append(menu1, "Testtesttest")

# Add some objects.
Button(mainFrame).Show()
CheckButton(mainFrame, check=True).Show()

# Now bring our color in!
clrcall = ColorManager() # Use custom path if you want (customfilepath param)
# or set clrcall.recursive_configure to True and run clrcall.autocolor_run(mainFrame)
clrcall.configure(mainFrame, True)

app.MainLoop()
```

Want to get widgets example? See the ```tests/``` foldder on our GitHub repo!