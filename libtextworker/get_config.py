"""
@package libtextworker.get_config
@brief Contains classes for generic INI files parsing
@since 0.1.3: Use CommentedConfigParser, but don't replace ConfigParser with it.
@since 0.1.4: Add json support; remake ConfigurationError class
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

    def __init__(self, path: str, msg: str, section: str, option: str = "\\not_specified\\"):
        full = "Configuration file {}, path [{}->{}]: {}"
        full = full.format(path, section, option, msg)
        super().__init__(full)

class GetConfig(ConfigParser):
    # Values
    yes_values: list = ["yes", "True", True]
    no_values: list = ["no", "False", False]

    aliases = {}
    detailedlogs: bool = True
    backups = {}

    for item in yes_values:
        aliases[item] = True

    for item in no_values:
        aliases[item] = False

    def __init__(self, config: dict[str] | str, file: str, **kwds):
        """
        A customized INI file parser.
        @param config (dict[str] or str) : Your stock settings, used to reset the file or do some comparisions
        @param file : Configuration file
        @param **kwds : To pass to configparser.ConfigParser (base class)

        When initialized, GetConfig loads all default configs (from config param) and store it in
        a dictionary for further actions (backup/restore file).

        @since 0.1.3: Allow config parameter as a str object
        @since 0.1.4: Allow importing+exporting configs as a json object
        """
        super().__init__(**kwds)

        self.cfg = {}

        if isinstance(config, str):
            self.read_string(config)
        else:
            self.read_dict(config)

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
    
    def full_backup(self, path:str, use_json: bool = False):
        """
        @since 0.1.4
        Do a full backup.
        @param path (str): Target backup file
        @param use_json (bool = False): Use the backup file in JSON format
        """
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
        @version Updated (parameters) on 0.1.3
        @version Updated return types on 0.1.4

        @param section, option: Target section->option
        @param needed (boolean=False): The target option is needed - should use with restore & noraiseexp.
        @param restore (boolean=False): Create the option if it is not found from the search
        @param noraiseexp (boolean=False): Make getkey() raise exceptions or not (when neccessary)
        @param raw (boolean=False): Don't use aliases for the value we get.

        @return False if the option does not exist and needed parameter set to False.
        """
        if not self.has_section(section):
            if needed == True:
                self.add_section(section)
            else:
                if not noraiseexp:
                    raise ConfigurationError(
                        self._file, "Section not found", section
                    )
                else:
                    return None

        if not option in self[section]:
            if needed == True:
                if restore == True:
                    self[section][option] = \
                        self.backups[section][option] \
                        if option in self.backups[section] \
                        else self.cfg[section][option]
                else:
                    self.set_and_update(section, option, self[section][option])
            else:
                if noraiseexp != True:
                    raise ConfigurationError(
                        self._file, "Option not found: %s" % option, section, option
                    )
                else:
                    return None

        value = self.get(section, option)

        if raw or not value.lower() in self.aliases:
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

    def move(
        self, list_: dict[str, dict[str, str]], delete_entire_section: bool = False
    ):
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

        ```list_``` parameter holds all configs to move. Each of options specified (section->option format)
        'is' a dictionary: sub-key 'newpath' specifies the location of the option to moved to (section->option format), 'file'
        specifies the new file to use (if needed, else use 'unchanged' or don't use the 'file' field).
        This function won't use backup(). Non-exist things will be ignored silently.

        If you use delete_entire_section, this func will REMOVE ALL sections found on the move. Only for ['file'] == 'unchanged'.
        """
        curr_sects = self.sections()
        newfile = ConfigParser()

        for item in list_:
            # Split and get values
            splits = item.split("->")
            if not splits[0] in curr_sects:
                break

            value = self.get(splits[0], splits[1])
            target = list_[item]["newpath"].split("->")

            if "file" not in list_[item]:
                target_file = "unchanged"
            else:
                target_file = list_[item]["file"]

            # Start the move
            if target_file == "unchanged":
                if not target[0] in self.sections():
                    self.add_section(target[0])

                self.set(target[0], target[1], value)

                if not delete_entire_section:
                    self.remove_option(splits[0], splits[1])
                else:
                    self.remove_section(splits[0])

                self.update()

            else:
                if os.path.isfile(target_file):
                    newfile.read(target_file)

                if not target[0] in newfile.sections():
                    newfile.add_section(target[0])

                newfile.set(target[0], target[1], value)

                with open(target_file, "w") as f:
                    newfile.write(f)

    def set_and_update(
        self, section: str, option: str, value: str | None = None
    ) -> None:
        """
        @since 0.1.3
        Set an option, and eventually apply it to the file.
        """
        self.set(section, option, value)
        self.update()
