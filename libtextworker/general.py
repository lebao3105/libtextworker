import logging
import os
import os.path
import pathlib
import platform

# Setup logging
DEBUG: bool = False
LOG_PATH = os.path.expanduser("~/libtew.log")

logger = logging.getLogger("libtextworker")

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
    def __init__(self, msg: str):
        logger.error(msg, exc_info=1)
        super().__init__(msg)


# Functions
if platform.system() == "Windows":
    separator = "\\"
else:
    separator = "/"

def CraftItems(path1: str or pathlib.Path, path2: str or pathlib.Path) -> str:
    return str(pathlib.Path(path1) / pathlib.Path(path2))


def CreateDirectory(directory: str, childs: list[str] = []):
    """
    Create a directory with optional sub-folders.
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
    I don't know how to describe this function.
    :raises Exception: Directory creation failed
    """
    directory = os.path.normpath(directory)
    splits = directory.split(separator)
    firstdir = splits[0]
    for item in range(1, len(splits)):
        firstdir += (separator + splits[item])
        if not os.path.isdir(firstdir):
            os.mkdir(firstdir)