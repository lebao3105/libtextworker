import importlib
import logging
import os
import pathlib
import shutil
import sys

from typing import Literal

# @since version 0.1.3
# Available GUI toolkits that this library supports
available_toolkits = Literal["tk", "wx"]

LOG_PATH = os.path.expanduser("~/.logs/libtew.log")
TOPLV_DIR = os.path.expanduser("~/.config/textworker")


# Classes
## Logging
class Logger(logging.Logger):
    UseToolKit: available_toolkits | bool = False

    def UseGUIToolKit(
        self, toolkit: available_toolkits
    ):  # Currently no Tkinter support
        self.UseToolKit = toolkit

    def CallGUILog(
        self,
        name: Literal["CRITICAL", "DEBUG", "ERROR", "EXCEPTION", "NORMAL", "WARNING"],
        msg: object,
        *args: object,
    ):
        """
        Call GUI toolkit logging function.
        """
        try:
            do = importlib.import_module(
                f"interface.{self.UseToolKit}.constants", "libtextworker"
            )
        except ImportError or ModuleNotFoundError:
            return
        else:
            getattr(do, "LOG_" + name)(msg, args)

    def critical(self, msg: object, *args: object, **kwds):
        super().critical(msg, *args, **kwds)
        self.CallGUILog("CRITICAL", msg, args)

    def debug(self, msg: object, *args: object, **kwds):
        super().debug(msg, *args, **kwds)
        self.CallGUILog("DEBUG", msg, args)

    def error(self, msg: object, *args: object, **kwds):
        super().error(msg, *args, **kwds)
        self.CallGUILog("ERROR", msg, args)

    def exception(self, msg: object, *args: object, **kwds):
        super().exception(msg, *args, **kwds)
        self.CallGUILog("EXCEPTION", msg, args)

    def log(self, level: int, msg: object, *args: object, **kwds):
        super().log(level, msg, *args, **kwds)
        self.CallGUILog("NORMAL", msg, args)

    def warning(self, msg: object, *args: object, **kwds):
        super().warning(msg, *args, **kwds)
        self.CallGUILog("WARNING", msg, args)


logger = Logger("textworker")


## Base Exception class
class libTewException(Exception):
    """
    Common exception class for libtextworker
    """

    def __init__(self, msg: str):
        logger.error(msg, exc_info=1)
        super().__init__(msg)


# Functions
def CraftItems(*args: str | pathlib.Path) -> str:
    """
    Craft any >=2 paths, together.
    @param *args (str|pathlib.Path)
    @return str: Result
    @raise Exception: not enough arguments (must be >=2)
    """
    if len(args) < 2:
        raise Exception("Not enough arguments")

    final = pathlib.Path(args[0])

    for i in range(1, len(args)):
        final /= str(args[i])

    return os.path.abspath(final)


def CreateDirectory(directory: str, childs: list[str] = []):
    """
    Create a directory with optional sub-folders.
    @param directory (str): Directory to create
    @param childs (list of str): Sub-dirs under $directory
    @throws Exception: Directory creation failed
    """
    if not os.path.isdir(directory):
        os.mkdir(directory)
    if childs:
        for folder in childs:
            folder = CraftItems(directory, folder)
            if not os.path.isdir(folder):
                os.mkdir(folder)


def WalkCreation(directory: str):
    """
    Create directory layer-to-layer.
    How to understand this? Try this path: path1/path2/path3.
    WalkCreation will create path1 first, then path1/path2 and path1/path2/path3. Skip existing dirs, of course.

    @param directory (str): Directory to create
    @throws Exception: Directory creation failed
    """
    directory = directory.replace("\\", "/")
    splits = directory.split("/")
    firstdir = splits[0]
    for item in range(1, len(splits)):
        firstdir += "/" + splits[item]
        if not os.path.isdir(firstdir):
            os.mkdir(firstdir)


def GetCurrentDir(file: str, aspathobj: bool = False):
    """
    Get the current directory path.
    @param file (str): File path
    @param aspathobj (bool): Return a pathlib.Path object instead of a string.
    @return pathlib.Path | str
    """
    result = pathlib.Path(file).parent
    if aspathobj:
        return result
    return result.__str__()


def ResetEveryConfig():
    """
    Reset every configurations under $TOPLV_DIR to default.
    Will close the app after completed.
    @see TOPLV_DIR
    """
    if os.path.isdir(TOPLV_DIR):
        shutil.rmtree(TOPLV_DIR)
    CreateDirectory(TOPLV_DIR)
    sys.exit()
