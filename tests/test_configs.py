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
        "section2": {"option1": "yes"}
    }

    cfgs = GetConfig(cfg, "helloworld/one/configs/configs.ini", False)
    cfgs.set("section1", "option1", "value_changed")
    assert cfgs["section1"]["option1"] == "value_changed"
    
    cfgs.Update()
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

    assert cfgs["section_one"]["option1"] == "value_changed"
    cfgs.read_file("helloworld/one/configs/new.ini")
    assert cfgs["test_move"]["section2_opt1"] in cfgs.yes_values

    cfgs.BackUp(['section_one->option1'])
    cfgs.Reset(True)
    assert cfgs['section_one']['option1'] == 'value_changed'