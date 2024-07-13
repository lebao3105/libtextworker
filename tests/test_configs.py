#	A cross-platform library for Python apps.
#	Copyright (C) 2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.
import os.path

# Testers: Don't import test_import, it will break pytest
from libtextworker.general import CreateDirectory, WalkCreation, CraftItems
from libtextworker.get_config import GetConfig


def test_makedirs():
    CreateDirectory("helloworld", ["one", "two", "three"])
    WalkCreation("helloworld/one/configs")
    WalkCreation(CraftItems("helloworld/two", "test"))

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
    assert cfgs.getkey("section1", "option1", True, True, True) == "value"
    cfgs.set("section1", "option1", "value_changed")
    assert cfgs.getkey("section1", "option1") == "value_changed"
    
    cfgs.update_and_write()
    cfgs.move(
        {
            "section1->option1": {
                "newpath": "section_one->option1",
                "file": "unchanged",
            },
            "section2->option1": {
                "newpath": "test_move->section2_opt1",
                "file": "helloworld/one/configs/new.ini",
            },
        }
    )

    assert cfgs.getkey("section_one", "option1") == "value_changed"
    assert cfgs.BackUp(["section_one->option1"], {}, True) == {"section_one": {"option1": "value_changed"}}

    cfgs.readf("helloworld/one/configs/new.ini")
    assert cfgs.getkey("test_move", "section2_opt1") in cfgs.yes_values
