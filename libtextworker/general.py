import logging
import os
import os.path
import pathlib
import platform
import shutil
import sys

if platform.system() == "Windows":
    separator = "\\"
else:
    separator = "/"

# Setup logging
DEBUG: bool = False
LOG_PATH = os.path.expanduser("~/libtew.log")

logger = logging.getLogger("textworker")

console_hdlr = logging.StreamHandler()
file_hdlr = logging.FileHandler(LOG_PATH)
formatter = logging.Formatter("%(asctime)s %(name)s->%(levelname)s : %(message)s")

console_hdlr.setLevel(logging.DEBUG)
console_hdlr.setFormatter(formatter)
file_hdlr.setLevel(logging.DEBUG)
file_hdlr.setFormatter(formatter)

logger.addHandler(console_hdlr)
logger.addHandler(file_hdlr)


# Classes
class libTewException(Exception):
    """
    Common exception class for libtextworker
    """

    def __init__(self, msg: str):
        logger.error(msg, exc_info=1)
        super().__init__(msg)


# Functions
def CraftItems(path1: str or pathlib.Path, path2: str or pathlib.Path) -> str:
    """
    Craft 2 paths together.
    @param path1 (str|pathlib.Path)
    @param path2 (str|pathlib.Path)
    @return str: Result
    """
    return str(pathlib.Path(path1) / pathlib.Path(path2))


def CreateDirectory(directory: str, childs: list[str] = []):
    """
    Create a directory with optional sub-folders.
    @param directory (str): Directory to create
    @param childs (list of str): Sub-dirs under @directory
    @raise Exception: Directory creation failed
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
    WalkCreation will create path1 first, then path2 and path3. Skip existing dirs, yes of course.

    @param directory (str): Directory to create
    @raise Exception: Directory creation failed
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
    @param aspathobj (bool): Return pathlib.Path type instead of a string.
    @return pathlib.Path | str
    """
    result = pathlib.Path(file).parent
    if aspathobj:
        return result
    return result.__str__()


def ResetEveryConfig():
    """
    Reset every configurations under ~/.config/textworker to default.
    Will close the app after completed.
    """
    shutil.rmtree(os.path.expanduser("~/.config/textworker"), ignore_errors=True)
    CreateDirectory(os.path.expanduser("~/.config/textworker"))
    sys.exit()
