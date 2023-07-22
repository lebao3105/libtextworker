"""
@package libtextworker.get_config
@brief Contains classes for generic INI files parsing
@since 0.1.3: Use CommentedConfigParser, but don't replace ConfigParser with it.
@since 0.1.4: Add json support; remake ConfigurationError class

See the documentation in /usage/getconfig.
"""
import json
import os
import typing

from .general import WalkCreation, libTewException

__all__ = ["ConfigurationError", "GetConfig"]

try:
    from commentedconfigparser import CommentedConfigParser as ConfigParser
except ImportError:
    from configparser import ConfigParser


class ConfigurationError(libTewException):
    def __init__(
        self, path: str, msg: str, section: str, option: str = "\\not_specified\\"
    ):
        full = "Configuration file {}, path [{}->{}]: {}"
        full = full.format(path, section, option, msg)
        super().__init__(full)


class GetConfig(ConfigParser):
    # Values
    yes_values: list = ["yes", "True", True, "1", 1, "on"]
    no_values: list = ["no", "False", False, "0", 0, "off"]

    aliases = {}
    detailedlogs: bool = True
    backups = {}
    cfg = {}

    for item in yes_values:
        aliases[item] = True

    for item in no_values:
        aliases[item] = False

    def __init__(self, config: dict[str] | str | None, file: str, **kwds):
        """
        A customized INI file parser.
        @param config (dict[str] or str) : Your stock settings, used to reset the file or do some comparisions
        @param file : Configuration file
        @param **kwds : To pass to configparser.ConfigParser (base class)

        When initialized, GetConfig loads all default configs (from config param) and store it in
        a dictionary for further actions (backup/restore file).

        @since 0.1.3: Allow config parameter as a str object
        @since 0.1.4: Allow importing+exporting configs as a json object, allow config param to be None
        """
        super().__init__(**kwds)

        if isinstance(config, str):
            self.read_string(config)
        elif isinstance(config, dict):
            self.read_dict(config)

        if config != None:
            for key in self:
                self.cfg[key] = self[key]

        self.readf(file)
        self._file = file

    # File tasks
    def readf(self, file: str, encoding: str | None = None):
        WalkCreation(os.path.dirname(file))
        if not os.path.exists(file):
            self.write(open(file, "w"))
        else:
            try:
                self.read_dict(json.loads(open(file, "r").read()))
            except:
                self.read(file, encoding)

        self._file = file

    def reset(self, restore: bool = False):
        os.remove(self._file)
        for key in self.cfg:
            self[key] = self.cfg[key]

        if restore and self.backups:
            for key in self.backups:
                self[key] = self.backups[key]

        self.update()

    def update(self):
        with open(self._file, "w") as f:
            self.write(f)
        self.read(self._file)

    # Options
    def backup(self, keys: dict, direct_to_keys: bool = False) -> dict:
        """
        Backs up user data, specified by the keys parameter (dictionary).
        Returns the successfully *updated* dictionary (if direct_to_keys param is True),
        or the self-made dict.
        """
        for key in keys:
            for subelm in keys[key]:
                if direct_to_keys == True:
                    keys[key][subelm] = self[key][subelm]
                    return keys
                else:
                    self.backups[key][subelm] = self[key][subelm]
                    return self.backups

    def full_backup(self, path: str, use_json: bool = False):
        """
        @since 0.1.4
        Do a full backup.
        @param path (str): Target backup file
        @param use_json (bool = False): Use the backup file in JSON format
        """
        if path == self._file:
            raise Exception("GetConfig.full_backup: filepath must be the loaded file!")
        
        with open(path, "w") as f:
            if use_json:
                json.dump(self, f)
            else:
                self.write(f)

    def getkey(
        self,
        section: str,
        option: str,
        needed: bool = False,
        restore: bool = False,
        noraiseexp: bool = False,
        raw: bool = False,
    ) -> typing.Any | None:
        """
        Try to get the value of an option under the spectified section.

        @param section, option: Target section->option
        @param needed (boolean=False): The target option is needed - should use with restore & noraiseexp.
        @param restore (boolean=False): Create the option if it is not found from the search
        @param noraiseexp (boolean=False): Make getkey() raise exceptions or not (when neccessary)
        @param raw (boolean=False): Don't use aliases for the value we get.

        @return False if the option does not exist and needed parameter set to False.
        """

        def bringitback():
            if needed:
                if restore:
                    try:
                        self.add_section(section)
                    except:
                        pass
                if not section in self.backups:
                    raise ConfigurationError(
                        self._file, "Section not found in the backup", section
                    )
                elif not option in self.backups:
                    raise ConfigurationError(
                        self._file, "Value not found in the backup", section, option
                    )
                self.set(section, option, self.backups[section][option])
            if restore:
                self.update()
            return self.backups[section][option]

        try:
            value = self.get(section, option)
        except:
            if noraiseexp:
                value = bringitback()
            else:
                raise ConfigurationError(
                    self._file, "Section or option not found", section, option
                )

        # Remove ' / "
        trans = ["'", '"']
        for key in trans:
            value = value.removeprefix(key).removesuffix(key)

        if not value in self.aliases or raw is True:
            return value
        else:
            return self.aliases[value]

    def aliasyesno(self, yesvalue=None, novalue=None) -> None:
        if yesvalue:
            self.yes_values.append(yesvalue)
            self.aliases[yesvalue] = True

        if novalue:
            self.no_values.append(novalue)
            self.aliases[novalue] = False

    def alias(self, value, value2) -> None:
        self.aliases[value] = value2

    def move(self, list_: dict[str, dict[str, str]]):
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

            if not section_ in self.sections():
                raise ConfigurationError(self._file, "Section not found", section_)
            if not option_ in self[section]:
                raise ConfigurationError(
                    self._file, "Option not found", section_, option_
                )

            value = self[section_][option_]

            # Start
            newsection = list_[section]["newpath"].split("->")[0]
            newoption = list_[section]["newpath"].split("->")[1]
            if not "file" in list_[section] or list_[section]["file"] == "unchanged":
                if not newsection in self.sections():
                    self.add_section(newsection)
                self.set_and_update(newsection, newoption, value)
            else:
                newobj = GetConfig(None, list_[section]["file"])
                newobj.add_section(newsection)
                newobj.set_and_update(newsection, newoption, value)

            if (
                "delete_entire_section" in list_[section]
                and list_[section_]["delete_entire_section"] == "yes"
            ):
                self.remove_section(section_)

    def set_and_update(
        self, section: str, option: str, value: str | None = None
    ) -> None:
        """
        @since 0.1.3
        Set an option, and eventually apply it to the file.
        """
        self.set(section, option, value)
        self.update()
