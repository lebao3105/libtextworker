"""
@package libtextworker.general
@brief Utilities (unable to describe)
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import logging
import os
import pathlib
import shutil
import sys
import warnings

from importlib import import_module
from typing import Literal

# @since version 0.1.3
# Available GUI toolkits that this library supports
available_toolkits = Literal["tk", "wx"]

Importable = {}
TOPLV_DIR = ""

# Classes

## Logging
class Logger(logging.Logger):
    """
    A logging class for GUIs.
    Available toolkits can be checked/set by the UseToolKit attribute.
    """

    UseToolKit: available_toolkits | bool = False

    def UseGUIToolKit(self, toolkit: available_toolkits):
        """
        Set's the GUI toolkit to use.
        Currently there is no support for Tkinter yet.
        """
        self.UseToolKit = toolkit

    def CallGUILog(self, name: Literal["CRITICAL", "DEBUG", "ERROR", "EXCEPTION", "NORMAL", "WARNING"], 
                   msg: object, *args: object):
        """
        Call GUI toolkit logging function.
        Do nothing if not able to.
        """
        if not self.UseToolKit: return
        do = import_module(f"libtextworker.interface.{self.UseToolKit}.constants")
        if args: msg = msg % args
        getattr(do, "LOG_" + name)(msg)

    def critical(self, msg: object, *args: object, **kwds):
        super().critical(msg, *args, **kwds)
        self.CallGUILog("CRITICAL", msg, *args)

    def debug(self, msg: object, *args: object, **kwds):
        super().debug(msg, *args, **kwds)
        self.CallGUILog("DEBUG", msg, *args)

    def error(self, msg: object, *args: object, **kwds):
        super().error(msg, *args, **kwds)
        self.CallGUILog("ERROR", msg, *args)

    def exception(self, msg: object, *args: object, **kwds):
        super().exception(msg, *args, **kwds)
        self.CallGUILog("EXCEPTION", msg, *args)

    def log(self, level: int, msg: object, *args: object, **kwds):
        super().log(level, msg, *args, **kwds)
        self.CallGUILog("NORMAL", msg, *args)

    def warning(self, msg: object, *args: object, **kwds):
        super().warning(msg, *args, **kwds)
        self.CallGUILog("WARNING", msg, *args)

## Base Exception class
class libTewException(Exception):
    """
    Common exception class for libtextworker
    """

    def __init__(this, msg: str):
        logger.error(msg, exc_info=1)
        Exception.__init__(this, msg)


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

    # Why I didn't know this earlier?
    # os.path.abspath(path) = os.path.normpath(os.path.join(os.getcwd() + path))
    # Yeah
    return os.path.normpath(final)


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


def test_import(pkgname: str) -> bool:
    """
    Tests if the specified module name is importable.
    Results is stored in Importable (dict[str, bool]).
    @see Importable
    """
    try:
        import_module(pkgname)
    except ImportError:
        Importable[pkgname] = False
        warnings.warn("%s not found" % pkgname)
        return False
    else:
        Importable[pkgname] = True
        return True

## Logging setup
## Only for libtextworker!
logger = Logger("libtextworker", logging.INFO)
logging.captureWarnings(True)
formatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s")

### Log to stream (sys.stdout/stderr)
strhdlr = logging.StreamHandler()
strhdlr.setFormatter(formatter)

### Log to file
from time import strftime, localtime
logpath = os.path.expanduser(f"~/.logs/libtextworker-{strftime(r'%Y-%m-%d', localtime())}.log")
CreateDirectory(os.path.dirname(logpath))
if not os.path.isfile(logpath): open(logpath, "w").write("")

filehdlr = logging.FileHandler(logpath)
filehdlr.setFormatter(formatter)

logger.addHandler(strhdlr)
logger.addHandler(filehdlr)