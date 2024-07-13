# Packaging libtextworker

## Git submodule

If needed, you can include libtextworker as a git submodule. Use a specific commit, or checkout to a branch/tag.

## Load the package from a different location

Modify ```sys.path``` or use import-helper tools such as ```importlib``` or ```imptools``` on Pypi. This is helpful to load the right library version/test features.

## Packaging with PyInstaller

Use the following flag:
```bash
--add-data "<absolute path to the library>"<separator>"<where you want to place>"
```

Explain:

* ```<absolute path to the library>```: Where libtextworker is installed.

* ```<separator>```: According to the PyInstaller document, you will use `;` if you're on Windows, otherwise use `:`.

* ```<where you want to place>```: The location of the library when it is packed with PyInstaller.

You can use this with other packages too.

## Packaging with for-Pypi build systems

Just like any packages else.