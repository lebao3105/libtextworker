# GetConfig class

## What is it?

Located in ```libtextworker.get_config```, GetConfig is a class which gives the user more power managing their configuration files - both JSON end INI format.

## How to use

### Basic usage 

Firstly, install ```configparser``` or ```commented-configparser``` (saves infile comments) from Pypi.

Now make a new instance of GetConfig with your configs & file preloaded:

```python
>>> import os
>>> cfgs: dict[str] = ...
>>> target = os.path.expanduser("~/.config/myfancy.cfg")
>>> from libtextworker.get_config import GetConfig
>>> cfger = GetConfig(config, file)
```

In the snippet above, ```cfgs``` is a dictionary contains all your defaults for restore/compare(WIP?) purposes; ```target``` is the path to the current settings file. Both 2 of them are passed into a new GetConfig instance (```cfger```).

But since GetConfig derived from ConfigParser class (even you use Commented-configparser), you can add more to your liking (below are some of them, the most usefuls):

* inline_comment_prefixes: Just like what it says - defaults disabled
* comment_prefixes: Normal comment prefixes (outline) - defaults to "#" and ";" as INI standards
* allow_no_value: Defaults disabled, allow options with no value inside
* delimeters: Option - value delimeters (defaults to "=" and ":") <1>

**<1>** this means you can do this in INI:
```ini
[section]
option = value
       ^ this is a delimeter
option2 : value
        ^ this is a delimeter too
```

How about JSON support?

Well, just do the same as INI.

Now you can do anything you like.

### New features

GetConfig extends ConfigParser with these features:

* Backup/reset settings;
* JSON support as said above;
* Run-time update - to a dictionary (GetConfig.backup) and/or to a file (GetConfig.full_backup);
* Advanced value getter with auto restore & alias feature (GetConfig.getkey);
* Move any thing to a new section, new option, or even to another file! (GetConfig.move);
* Watch file system change!

These features makes GetConfig an unique thing you must see:)

A planned thing: GetConfig will use ```watchdog``` [module](https://pypi.org/project/watchdog) to dynamically notify the user when the file is changed outside, also an option to chose whetever to load the changes or not.

One more thing is the real restore (have I said this is available before?) previous user options. They should be available on 0.1.4 release.

> Why "real"? Because the previous "restore" function (if it exists) not really something even "real" - you have to use move() function. Whatever... you still can.

GetConfig is the core of ColorManager, a class for GUIs in libtextworker.

To master everything you got from GetConfig, read all functions description and use they for your purpose.