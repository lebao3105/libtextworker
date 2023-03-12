from libtextworker import Importable

if Importable["interface.wx"] == True:
    pass
else:
    raise Exception("interface.wx is called but its dependency wxPython is not installed")