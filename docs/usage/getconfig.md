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
>>> cfger = GetConfig(cfgs, file, True)
```

In the snippet above, ```cfgs``` is a dictionary contains all your defaults for restore/compare(WIP?) purposes; ```target``` is the path to the current settings file. Both 2 of them are passed into a new GetConfig instance (```cfger```).

The last argument will tell GetConfig to watch and reread the file if an even happends to the file.

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

You can use JSON as the content to load/default settings.

GetConfig has no dictionary object support, for both INI and JSON reads. The returned object will be a string, cast to dictionary with `eval()` or `json.loads()`.

### New features

GetConfig extends ConfigParser with these features:

* Backup/reset settings;
* JSON read (write just use `json.dumps()`);
* Run-time update - to a dictionary (`GetConfig.BackUp`);
* Advanced value getter (`GetConfig.getkey`);
* Aliases support (`GetConfig.alias*`);
* Move any thing to a new section, new option, or even to another file! (`GetConfig.move`);
* Watch file system change!

~A planned thing~ Implemented: GetConfig will use ```watchdog``` [module](https://pypi.org/project/watchdog) to dynamically notify the user when the file is changed outside, also ~an option to chose whetever to~ load the changes ~or not~. Overriding `GetConfig.on_any_event` to anything you want to do on file system event(s).

Futher documentation on this please look at watchdog's documentation.

GetConfig is the core of ColorManager, a class for GUIs in libtextworker.

To master everything you got from GetConfig, read all functions description, as well as `ConfigParser` documentation.