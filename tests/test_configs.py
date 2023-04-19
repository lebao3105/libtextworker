import os.path
from libtextworker.general import *
from libtextworker.get_config import GetConfig


def test_makedirs():
    CreateDirectory("helloworld", ["one", "two", "three"])
    WalkCreation("helloworld/one/configs")
    WalkCreation(CraftItems("helloworld/two", "\\test"))

    open("helloworld/.gitignore", "w").write("*")

    assert os.path.isdir("helloworld/one") == True
    assert os.path.isdir("helloworld/one/configs") == True
    assert os.path.isdir("helloworld/two") == True
    assert os.path.isdir("helloworld/two/test") == True
    assert os.path.isdir("helloworld/three") == True


def test_mkconfig():
    cfg = {
        "section1": {"option1": "value", "option2": "2"},
        "section2": {"option1": "yes"},
    }

    cfgs = GetConfig(cfg, "helloworld/one/configs/configs.ini")
    cfgs.set("section1", "option1", "value_changed")
    cfgs.update()

    assert cfgs.getkey("section1", "option1") == "value_changed"
    assert cfgs.getkey("section2", "option1") == "yes"
