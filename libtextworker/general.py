import importlib
import logging
import os
import os.path
import pathlib
import platform
import shutil
import sys

from typing import Literal

if platform.system() == "Windows":
    separator = "\\"
else:
    separator = "/"

# @since version 0.1.3
available_toolkits = Literal[
    'tk',
    'wx'
]

# Logging
class Logger(logging.Logger):

    def UseGUIToolKit(self, toolkit: available_toolkits): # Currently no Tkinter support
        self.UseToolKit = toolkit

    def critical(self, msg: object, *args: object, **kwds):
        super().critical(msg, *args, **kwds)
        try:
            do = importlib.import_module(f"interface.{self.UseToolKit}.constants", "libtextworker")
        except ImportError:
            return
        else:
            getattr(do, "LOG_CRITICAL")(msg)
    
    def debug(self, msg: object, *args: object, **kwds):
        super().debug(msg, *args, **kwds)
        try:
            do = importlib.import_module(f"interface.{self.UseToolKit}.constants", "libtextworker")
        except ImportError:
            return
        else:
            getattr(do, "LOG_DEBUG")(msg)

    def error(self, msg: object, *args: object, **kwds):
        super().error(msg, *args, **kwds)
        try:
            do = importlib.import_module(f"interface.{self.UseToolKit}.constants", "libtextworker")
        except ImportError:
            return
        else:
            getattr(do, "LOG_ERROR")(msg)
    
    def exception(self, msg: object, *args: object, **kwds):
        super().exception(msg, *args, **kwds)
        try:
            do = importlib.import_module(f"interface.{self.UseToolKit}.constants", "libtextworker")
        except ImportError:
            return
        else:
            getattr(do, "LOG_EXCEPTION")(msg)
            
    def log(self, level: int, msg: object, *args: object, **kwds):
        super().log(level, msg, *args, **kwds)
        try:
            do = importlib.import_module(f"interface.{self.UseToolKit}.constants", "libtextworker")
        except ImportError:
            return
        else:
            getattr(do, "LOG_NORMAL")(msg)
    
    def warning(self, msg: object, *args: object, **kwds):
        super().warning(msg, *args, **kwds)
        try:
            do = importlib.import_module(f"interface.{self.UseToolKit}.constants", "libtextworker")
        except ImportError:
            return
        else:
            getattr(do, "LOG_WARNING")(msg)
    
LOG_PATH = os.path.expanduser("~/.logs/libtew.log")
TOPLV_DIR = os.path.expanduser("~/.config/textworker")
logger = Logger("textworker")

# Classes
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
    """
    new = list(args)

    for i in range(0, len(new)):
        new[i] = str(new[i]).replace("\\", "/")

    final = pathlib.Path(new[0])

    for i in range(1, len(new)):
        new[i] = str(new[i]).removeprefix("/").removesuffix("/")
        final /= new[i]
    return str(final)


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
    directory = os.path.normpath(directory)
    splits = directory.split(separator)
    firstdir = splits[0]
    for item in range(1, len(splits)):
        firstdir += separator + splits[item]
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
