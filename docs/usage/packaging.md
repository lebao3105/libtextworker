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

* <absolute path to the library>: Where libtextworker is installed.

* <separator>: According to the PyInstaller document, you will use ; if you're on Windows, otherwise use :.

* <where you want to place>: The location of the library when it is packed with PyInstaller.

You can use this with other packages too.

## Packaging with poetry

Add libtextworker like any other packages:

```bash
    $ poetry add libtextworker
```

If you want to use the library from a specific path, so instead of running the command above, add this to your ```[tool.poetry.dependencies]```:

```toml
libtextworker = {path = "path_to_the_lib", extras = ["what_you_want"]}
```

But if you use libtextworker as a git submodule and want to publish your project to (Test)Pypi (like me), then you shouldn't pack the submodule like that. You should use the git way (modify pyproject.toml):

```toml
libtextworker = { git = "https://github.com/lebao3105/libtextworker.git", ..., extras = ["extra"] }
```

Why "..."? It's your option:

* ```rev```: Git revision, use a specific commit hash
* ```tag```: Git tag
* ```branch```: Git branch