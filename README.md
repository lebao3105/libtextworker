## libtextworker

## Implemented things
* Custom ```wx.stc.StyledTextCtrl``` with custom configs (right-click menu, tab indentation and line number)
* A class for building UI from XML file (XRC) (taken from textworker)
* A function for wx.MenuBar to create menu items faster (from textworker)

## Usage
Add this to your ```requirements.txt```:
```
-e git+https://github.com/lebao3105/libtextworker.git#egg=libtextworker
```

Look at the project structure:
* ```general```: Contain the base exception class for the project and some unique functions about directory creations.
* ```get_config```: Ported from textworker, contains a class that can handle .ini files
* ```interface.manager```: Contains ColorManager class which is used to sync the application with the system color.
* ```interface.* (sub-folders)```: Widget for **"specific"** UI platform (wxPython for now)

## Todos
* Custom config files
* Support for Tkinter?
