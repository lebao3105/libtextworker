# Actually this is not a test script.
# It is used to clean all outputs.
import pathlib
import pytest
import shutil

@pytest.mark.order('last')
def test_clean():
    shutil.rmtree(str(pathlib.Path(__file__).parent / '..' / 'helloworld'))
