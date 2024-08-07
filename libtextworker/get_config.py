"""
@package libtextworker.get_config
@brief Contains classes for generic INI files parsing

See the documentation in /usage/getconfig.
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import json
import os
import typing

from .general import Importable, WalkCreation, libTewException
from warnings import warn

__all__ = ["ConfigurationError", "GetConfig"]

if Importable["commentedconfigparser"]:
    from commentedconfigparser import CommentedConfigParser as ConfigParser
elif Importable["configparser"]:
    from configparser import ConfigParser
else:
    warn("GetConfig is only able to use JSON files - required dependency for INI is not installed")

if Importable["watchdog"]:
    from watchdog.observers import Observer
    from watchdog.events import *


class ConfigurationError(libTewException):
    """
    As the name says, class for (mostly) GetConfig exceptions.
    """
    def __init__(this, path: str, msg: str, section: str,
                 option: str = "\\not specified\\", value: str = ""):
        
        full = "Configuration file {},\n-> [{}->{}{}]: {}"
        full = full.format(path, section, option, f'={value}' if value else '', msg)
        libTewException.__init__(this, full)

class GetConfig(ConfigParser):

    # Positive values - they're aliases of True
    yes_values = [ 'yes', 'true', '1', 'on', 1, True ]

    # Negative values - they're aliases of False
    no_values = [ 'no', 'false', '0', 'off', 0, False, '', None ]

    # OEM settings
    OEM: dict[str] = {}

    # Aliases
    aliases: dict = {}

    # Read file
    _file: str

    # Backups
    _backups: dict[str] = {}

    # Use watchdog for file events watching
    addWatchDog: bool

    
    def __init__(this, defaults: dict[str] | str | None, load: str | dict[str],
                 watchChanges: bool = False, **kwds):
        """
        Constructor.
        """

        ConfigParser.__init__(this, **kwds)

        if isinstance(defaults, str):
            try:
                this.OEM = json.loads(defaults)
            except:
                new = GetConfig(defaults=None, load=defaults)
                for key in new.sections():
                    this.OEM[key] = dict(new[key])
        elif defaults:
            this.OEM = defaults.copy()
            
        this.addWatchDog = watchChanges and Importable['watchdog']

        # For getboolean
        for yes in this.yes_values:
            if isinstance(yes, str):
                this.BOOLEAN_STATES[yes] = True
                this.aliases[yes] = True
                
        for no in this.no_values:
            if isinstance(yes, str):
                this.BOOLEAN_STATES[no] = False
                this.aliases[no] = False

        if this.addWatchDog:
            this._evtHdlr = FileSystemEventHandler()
            this._evtHdlr.on_any_event = this.on_any_event

            this._observer: Observer # type: ignore

        if isinstance(load, str):
            try:
                this.read_string(load)
            except:
                this.readf(load)

        elif isinstance(load, dict):
            this.read_dict(load)
    
    def __del__(this):
        """
        Destructor.
        """

        if this.addWatchDog:
            if this._observer.is_alive():
                this._observer.stop()
                this._observer.join()
    
    def read_string(this, string: str):
        """
        Reads a string. String in dictionary/JSON style is supported.

        For reading a file, using either read() or read_file().
        """

        try:
            this.read_dict(json.loads(string))
        except:
            ConfigParser.read_string(this, string)

    def readf(this, file: str, encoding: str = "utf8"):
        """
        Reads a file.
        """

        WalkCreation(os.path.dirname(file))
        if not os.path.isfile(file):
            open(file, "w")

        this.read(file, encoding)
        this._file = file

        if this.addWatchDog:
            this._observer = Observer()
            this._observer.schedule(this._evtHdlr, file)
            this._observer.start()


    def Reset(this, restore: bool, backupdelimiter: str = "->"):
        """
        Resets GetConfig and loaded file to default settings.
        Also restores the last backup if able and restore parameter is True.

        @param restore (bool): Restores the last backup
        @param backupdelimiter (str): Path delimiter (defaults to ->) used in the last backup
        """
        os.remove(this._file)
        this.clear()

        if this.OEM: this.read_dict(this.OEM)
        if restore:
            if this._backups:
                for key, value in this._backups:
                    splits = key.split(backupdelimiter)
                    assert len(splits) == 2, "Incomplete setting path or has more than one delimiter"

                    if not this.has_section(splits[0]): this.add_section(splits[0])
                    this[splits[0]][splits[1]] = value
            else:
                raise ValueError("No backups were made!")
    
    def update_and_write(this):
        """
        Updates and write new changes into the current file.
        @see update
        """
        ConfigParser.update(this)
        this.write(open(this._file, "w"))
                    
    def move(this, list_: dict[str, dict[str, str]]):
        """
        @since 0.1.3

        Move configurations found from the file that GetConfig currently uses.
        Below is an example:
        ```
        move(
            list_={
                "section1->option1": {
                    "newpath": "section_one->option1",
                    "file": "unchanged"
                },
                "special->option0": {
                    "newpath": "special_thing->option0",
                    "file": "~/.config/test.ini"
                }
            }
        )
        ```

        "list_" is a dictionary - each key is a dictionary which defines how a setting should be moved.
        The key name is your setting (section->option). Under that 'key' is 2 options:
        * "newpath" specifies the location of the setting in the target file (section->option)
        * "file" specifies the location of the target file we'll move the options to. Ignore it or leave it "unchanged" to tell
            the function that you don't want to move the setting else where than the current file.
        * "delete_entire_section" (ignorable, values are 'yes' and 'no') allows you to remove the old section after the move.
        """

        for section in list_.keys():
            # Prepare for the move
            section_ = section.split("->")[0]
            option_ = section.split("->")[1]

            if not section_ in this:
                raise ConfigurationError(this._file, "Section not found", section_)
            if not option_ in this[section_]:
                raise ConfigurationError(this._file, "Option not found", section_, option_)

            value = this[section_][option_]

            # Start
            newsection = list_[section]["newpath"].split("->")[0]
            newoption = list_[section]["newpath"].split("->")[1]
            if not "file" in list_[section] or list_[section]["file"] == "unchanged":
                if not newsection in this.sections():
                    this.add_section(newsection)
                this.set_and_update(newsection, newoption, value)
            else:
                newobj = GetConfig(None, list_[section]["file"], False)
                if not newsection in newobj:
                    newobj.add_section(newsection)
                newobj.set_and_update(newsection, newoption, value)

            if "delete_entire_section" in list_[section] \
                and list_[section_]["delete_entire_section"] in this.yes_values:
                this.remove_section(section_)
    
    def aliasyesno(this, yesvalue=None, novalue=None):
        """
        Makes alias(es) of True/False/both.
        """
        if yesvalue:
            this.yes_values.append(yesvalue)
            this.aliases[yesvalue] = True

        if novalue:
            this.no_values.append(novalue)
            this.aliases[novalue] = False

    def alias(this, value, value2):
        """
        Makes an alias.
        """
        this.aliases[value] = value2
    
    def set_and_update(this, section: str, option: str, value: str | None = None):
        """
        @since 0.1.3
        Set an option, and eventually apply it to the file.
        """
        this.set(section, option, value)
        this.update_and_write()

    def BackUp(this, which: list[str], keys: dict[str, str], direct_to_keys: bool = False, delimeter: str = '->') -> dict:
        """
        Make a copy of values/sections

        @param which (list of strs): List of paths to the section/option to backup:
            * Separated by a "->" (without quotes);
            * If the path has list(s), use the number index (0-based) for the item \
                you want to take (e.g root->stores->0) will take the first item of the root->stores list.

        @see GetTheLastBackUp
        """

        target = this._backups if keys and direct_to_keys else keys

        for path in which:
            splits = path.split(delimeter)
            assert len(splits) == 2, \
                    f"{path} has either no delimiter or not enough/too much items to split.\n" \
                    "Also dictionary objects are not supported. If you have no dicitonary, " \
                    " change the delimiter so that BackUp won't confuse again."

            # Get the parent path and the option/section name
            name = splits[-1]
            parent = splits[0]
            
            if name.isdigit():
                if not parent in target.keys(): target[parent] = []
                name = int(name)
            else:
                if not parent in target.keys(): target[parent] = {}
            
            target[parent][name] = this[parent][name]

            return target
    
    def getkey(this, section: str, option: str, needed: bool = False,
               make: bool = False, noraiseexp: bool = False, raw: bool = False) -> typing.Any | None:
        """
        Try to get the value of an option under the spectified section.

        @param section, option: Target section->option
        @param needed (boolean=False): The target option is needed - should use with make & noraiseexp.
        @param make (boolean=False): Create the option if it is not found from the search
        @param noraiseexp (boolean=False): Make getkey() raise exceptions or not (when neccessary)
        @param raw (boolean=False): Don't use aliases for the value we get.

        @return False if the option does not exist and needed parameter set to False.
        """

        def bringitback():
            target = this._backups
            value_: typing.Any

            if make:
                if not target: target = this.OEM
                
                if not target[section]:
                    raise ConfigurationError(
                        this._file, f"Unable to find {section} section in both saved backups and default settings!",
                        section, option
                    )
                
                if not target[section][option]:
                    raise ConfigurationError(
                        this._file, f"Unable to find the option under {section} in both saved backups and default settings!",
                        section, option
                    )

                if not section in this.sections():
                    this.add_section(section)

                value_ = target[section][option]
                if needed:
                    this.set_and_update(section, option, value_)
                else:
                    this.set(section, option, value_)
                return value_

        try:
            value = this.get(section, option)
        except Exception as e:
            if noraiseexp: value = bringitback()
            else: raise e

        # Remove ' / "
        trans = ["'", '"']
        for key in trans:
            value = value.removeprefix(key).removesuffix(key)

        if (not value in this.aliases) or (raw is True):
            return value
        else:
            return this.aliases[value]
        
    """
    FileSystemEventHandler
    """

    if Importable["watchdog"]:
        def on_any_event(this, event: FileSystemEvent):
            if event.src_path != this._file: # Watchdog also catches events from other files
                return

            if isinstance(event, (FileModifiedEvent, FileCreatedEvent)):
                this.read_file(event.src_path)
            elif isinstance(event, (FileOpenedEvent, FileClosedEvent)):
                return
            else:
                warn(f"{event.src_path} has gone!")
    else:
        def on_any_event(this, event):
            raise NotImplementedError("Watchdog module is not usable")