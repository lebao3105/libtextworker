# First steps

## What version of libtextworker I want?

```python
# Assuming this is your __init__.py/main file
# Because the code below should be called first
# before any other libtextworker calls
from libtextworker.versioning import require
require("libtextworker", "0.1.4")
```

In the code above, we import the require function from the libtextworker.versioning module, then use it to "require" version 0.1.4 of libtextworker. This ensures that your project is using the library with version 0.1.4, nothing else.

Here's the ```require``` function:

```python
def require(project: str, target_version: str):
        """
        Ensures that a project is available for the requested version OR HIGHER.
        @param project (str): Project name
        @param target_version (str): Project version you want to have
        """
```

You can use this function for other packages, just make sure that the package has ```__version__``` attribute.

There are many functions for your use: `require_exact`, `require_lower`, and even `is_development_version`, `is_development_version_from_project` for verions type-checking.

Imported projects for version checking/getting are placed in `libtextworker.versioning.Requested`.

There is also a function called `test_import`, which returns a boolean. The test result will be added in a variable called `Importable`. You better use it before any (related) use of the target library

## Explore variables

The top-level module has some useful attributes:

* THEMES_DIR (str): Defaults to ```~/.configs/textworker/themes```; where all themes for GUIs are placed
* EDITOR_DIR (str): Defauls to ```~/.configs/textworker/editorconfigs/```; default configs directory for GUI editors
* Importable (dict[str, bool]): An alias to ```general.Importable```, contains check results for Python modules.

In libtextworker.general module we have a variable called `available_toolkits` (since 0.1.3), indicates supported GUI toolkits. Only wxPython and Tkinter are supported. Also we have LOG_PATH shows us where the log file is located, `TOPLV_DIR` for the top-level settings path.

## Choose what you want

Take a look at all library modules:

* ```general```: Has functions that mostly about file/directory touch. They are born to make file operations easier.
* ```get_config``` ported from texteditor, contains GetConfig class which is an advanced INI parser (json import/export ongoing), with backup, value aliases, and runtime update.
* ```versioning```: See above.
* ```interface.manager```: Contains ColorManager which handles GUI widgets color/font
* ```interface._colors``` (since 0.1.3) or `interface.colors` (since 0.1.4) names *some* colors.
* subfolders in ```interface```: GUIs support ('wx' for wxPython, 'tk' for Tkinter)

## Packaging

Head over to this [page](packaging.md).