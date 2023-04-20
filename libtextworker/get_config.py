import configparser
import os
import os.path

from .general import WalkCreation, libTewException

__all__ = ["ConfigurationError", "GetConfig"]


class ConfigurationError(libTewException):
    def __init__(self, section: str = "", option: str = "", msg: str = ""):
        prefix = "Error in the configuration file: "
        if not msg:
            msg = "*UNKNOW ERROR*"
        else:
            msg = "[{}->{}] : {}".format(
                section,
                "(None)" if option == "" else option,
                "No Message" if msg == "" else msg,
            )
        full = prefix + msg
        super().__init__(full)


class GetConfig(configparser.ConfigParser):
    # Values
    yes_values: list = ["yes", "True"]
    no_values: list = ["no", "False"]

    returnbool: bool = True
    aliases = {}
    detailedlogs: bool = True
    backups = {}

    def __init__(self, config: dict, file: str, **kwds):
        """
        A customized INI file parser.
        @param config : Default configurations, used to reset the file or do some comparisions
        @param file : Configuration file
        @param **kwds : To pass to configparser.ConfigParser (base class)

        When initialized, GetConfig loads all default configs (from config param) and store it in
        a dictionary for further actions (backup/restore file).
        """
        super().__init__(**kwds)

        self.cfg = {}

        for key in config:
            self[key] = config[key]
            self.cfg[key] = config[key]

        self.readf(file)
        self.__file = file

    # File tasks
    def readf(self, file: str, encoding: str | None = None):
        if os.path.isfile(file):
            self.read(file, encoding)
        else:
            firstdir = os.path.dirname(file)
            WalkCreation(firstdir)
            with open(file, mode="w") as f:
                try:
                    self.write(f)
                except OSError:
                    raise Exception("Unable to access to the file name %s" % file)
                else:
                    self.read(file, encoding)
        self.__file = file  # Should I?

    def reset(self, restore: bool = False) -> bool:
        try:
            os.remove(self.__file)
        except:
            return False
        else:
            for key in self.cfg:
                self[key] = self.cfg[key]

            if restore and self.backups:
                for key in self.backups:
                    self[key] = self.backups[key]

            with open(self.__file, mode="w") as f:
                self.write(f)
            return True

    def update(self):
        with open(self.__file, "w") as f:
            self.write(f)
        self.read(self.__file)

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

    def getkey(
        self,
        section: str,
        option: str,
        needed: bool = False,
        restore: bool = False,
        noraiseexp: bool = False,
        getbool: bool = returnbool,
    ) -> str | bool:
        """
        Try to get the value of an option under the spectified section.

        If the option does not exist and needed parameter is set to True,
        GetConfig will add that option automatically with the value based on
        its previously initialized configs. If restore parameter is set to True,
        GetConfig will use the backed up option, if possible.

        If you don't want to see exceptions raised and just need False (when something went wrong),
        set noraiseexp to True.

        Otherwise it will check for the value's alias, then return the value.
        """
        if not self.has_section(section):
            if needed == True:
                self.add_section(section)
            else:
                if noraiseexp != True:
                    raise ConfigurationError(
                        section, msg="Section not found: %s" % section
                    )
                else:
                    return False

        if not option in self[section]:
            if needed == True:
                if restore == True:
                    self.set(
                        section,
                        option,
                        self.backups[section][option]
                        if option in self.backups[section]
                        else self.cfg[section][option],
                    )
                else:
                    self.set(section, option, self[section][option])
            else:
                if noraiseexp != True:
                    raise ConfigurationError(
                        section, option, "Option not found: %s" % option
                    )
                else:
                    return False

        if needed == True:
            self.update()

        value = self.get(section, option)

        return value if value not in self.aliases else self.aliases[value]

    def aliasyesno(self, yesvalue, novalue, enable: bool = True) -> None:
        """
        Use a custom yes/no value, for example:
        There is an option under [section], and GetConfig will return
        True if the options is 'yes', False if the options is 'no'.
        You can change 'yes' and 'no' value for your use.
        If you dont want the parser return a boolean, set enable to false.
        """
        self.yes_values.append(yesvalue)
        self.no_values.append(novalue)
        self.returnbool = enable

    def alias(self, value, value2) -> None:
        self.aliases[value] = value2
