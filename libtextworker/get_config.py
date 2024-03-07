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

from .general import WalkCreation, libTewException
from warnings import warn
from watchdog.observers import Observer
from watchdog.events import *

__all__ = ["ConfigurationError", "GetConfig"]

try:
    from commentedconfigparser import CommentedConfigParser as ConfigParser
except ImportError:
    from configparser import ConfigParser

class ConfigurationError(libTewException):
    """
    As the name says, class for (mostly) GetConfig exceptions.
    """
    def __init__(this, path: str, msg: str, section: str,
                 option: str = "\\not_specified\\"):
        
        full = "Configuration file {}, path [{}->{}]: {}"
        full = full.format(path, section, option, msg)
        libTewException.__init__(this, full)

class GetConfig(ConfigParser):
    # Values
    yes_values: list = ["yes", "True", True, "1", 1, "on"]
    no_values: list = ["no", "False", False, "0", 0, "off"]

    aliases: dict = {}
    backups: dict = {}
    cfg: dict = {}
    detailedlogs: bool = True

    _evtHdlr = FileSystemEventHandler()
    _observer: Observer # type: ignore

    for item in yes_values:
        aliases[item] = True

    for item in no_values:
        aliases[item] = False

    def __init__(this, config: dict[str] | str | None, file: str, **kwds):
        """
        A customized INI file parser.
        @param config (dict[str] or str) : Your stock settings, used to reset the file or do some comparisions
        @param file : Configuration file
        @param **kwds : To pass to configparser.ConfigParser (base class)

        When initialized, GetConfig loads all default configs (from config parameter) and store it in
        a dictionary for further actions (backup/restore file).

        @since 0.1.3: Allow config parameter as a str object
        @since 0.1.4: JSON support, allow config parameter to be None, file system watch
        """
        ConfigParser.__init__(this, **kwds)

        if isinstance(config, str):
            this.read_string(config)
        elif isinstance(config, dict):
            this.read_dict(config)

        if config != None:
            for key in this:
                this.cfg[key] = this[key]

        this.readf(file)
        this._evtHdlr.on_any_event = this.on_any_event

    # File tasks
    def readf(this, file: str, encoding: str | None = None):
        """
        Reads all settings from a file.
        Mostly for application/GetConfig internal use.
        """
        WalkCreation(os.path.dirname(file))
        if not os.path.exists(file):
            this.write(open(file, "w"))
        else:
            try:
                this.read_dict(json.loads(open(file, "r").read()))
            except:
                this.read(file, encoding)

        this._file = file
        this._observer = Observer()
        this._observer.schedule(this._evtHdlr, file)
        this._observer.start()
    
    def __del__(this):
        if this._observer.is_alive():
            this._observer.stop()
            this._observer.join()

    def reset(this, restore: bool = False):
        """
        Loads default settings to GetConfig and loaded file.
        Also restore backups if restore is True and GetConfig.backups is not empty.
        """
        os.remove(this._file)
        for key in this.cfg:
            this[key] = this.cfg[key]

        if restore and this.backups:
            for key in this.backups:
                this[key] = this.backups[key]

        this.update()

    def update(this):
        """
        Writes current settings to loaded file.
        """
        with open(this._file, "w") as f:
            this.write(f)

    # Options
    def backup(this, keys: dict, direct_to_keys: bool = False) -> dict:
        """
        Backs up user data, specified by the keys parameter (dictionary).
        Returns the successfully *updated* dictionary (if direct_to_keys is True),
        or the self-made dict.
        """
        target = keys if direct_to_keys else this.backups
        for key in keys:
            target[key] = this[key]

        return target

    def full_backup(this, noFile: bool, path: str, use_json: bool = False):
        """
        @since 0.1.4
        Backup all settings by writing to GetConfig.backups and/or another file.
        @param noFile (bool): Don't write to any file else.
        @param path (str): Target backup file (defaults to the loaded one)
        @param use_json (bool = False): Use the backup file in JSON format
        """
        if not path:
            path = this._file
        
        for section in this.sections():
            this.backups[section] = this[section]

        if not noFile:
            with open(path, "w") as f:
                if use_json:
                    json.dump(this, f)
                else:
                    this.write(f)

    def restore(this, keys: dict[str, str] | None, optional_path: str):
        """
        @since 0.1.4
        Restore options.
        @param keys (dict[str, str] or None): Keys + options to restore.
            Optional but self.backups must not be empty.
        @param optional_path (str): The name says it all. If specified,
            both this path and self._file will be written.
        You can also use move() function for a more complex method.
        """

        if not keys and this.backups:
            raise AttributeError(
                "GetConfig.restore: this.backups and keys parameter are empty/died"
            )
        for key in keys:
            for option in keys[key]:
                this.set_and_update(key, option, keys[key][option])

        if optional_path:
            with open(optional_path, "w") as f:
                this.write(f)

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
            target = this.backups
            value_: typing.Any

            if make:
                if not target:
                    target = this.cfg
                if not target[section]:
                    raise ConfigurationError(this._file, "Unable to find the section in both GetConfig.backups and GetConfig.cfg!",
                                             section, option)
                if not target[section][option]:
                    raise ConfigurationError(this._file, "Unable to find the option in both GetConfig.backups and GetConfig.cfg!",
                                             section, option)
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
        except:
            if noraiseexp:
                value = bringitback()
                if not value:
                    return None
            else:
                raise ConfigurationError(this._file, "Section or option not found", section, option)

        # Remove ' / "
        trans = ["'", '"']
        for key in trans:
            value = value.removeprefix(key).removesuffix(key)

        if not value in this.aliases or raw is True:
            return value
        else:
            return this.aliases[value]

    def aliasyesno(this, yesvalue=None, novalue=None):
        if yesvalue:
            this.yes_values.append(yesvalue)
            this.aliases[yesvalue] = True

        if novalue:
            this.no_values.append(novalue)
            this.aliases[novalue] = False

    def alias(this, value, value2):
        this.aliases[value] = value2

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

            if not section_ in this.sections():
                raise ConfigurationError(this._file, "Section not found", section_)
            if not option_ in this[section]:
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
                newobj = GetConfig(None, list_[section]["file"])
                newobj.add_section(newsection)
                newobj.set_and_update(newsection, newoption, value)

            if "delete_entire_section" in list_[section] \
                and list_[section_]["delete_entire_section"] in this.yes_values:
                this.remove_section(section_)

    def set_and_update(this, section: str, option: str, value: str | None = None):
        """
        @since 0.1.3
        Set an option, and eventually apply it to the file.
        """
        this.set(section, option, value)
        this.update()

    """
    FileSystemEventHandler
    """

    def on_any_event(this, event: FileSystemEvent):
        if event.src_path != this._file: # Watchdog also catch events from other files
            return

        if isinstance(event, (FileModifiedEvent, FileCreatedEvent)):
            this.readf(event.src_path)
        elif isinstance(event, (FileOpenedEvent, FileClosedEvent)):
            return
        else:
            warn(f"{event.src_path} has gone!")
        
    
    
