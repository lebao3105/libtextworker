#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

# Actually this is not a test script.
# It is used to clean all outputs.
import pathlib
import pytest
import shutil


@pytest.mark.order("last")
def test_clean():
    shutil.rmtree(str(pathlib.Path(__file__).parent / ".." / "helloworld"))
