# Installing libtextworker

The latest version of this library is 0.1.3.

You will need:

* Python 3.8 or higher with pip installed - get it from [python.org](https://python.org)
* Basic Python & Python GUI programming knowledge - this is not really a project for beginners
* Your head should be cold, as this is a working-on project - changes and bugs will many

## Available packages

As of the 0.1.3 version, we have the following packages:

1. libtextworker: No GUI support, but ```_importer```, ```general``` and ```get_config```, ```versioning``` modules can still be used
2. libtextworker[autocolor]: Autocolor (depends on the system's color) support for GUI apps (available on 0.1.3+)
3. libtextworker[tkinter]: Install requirements for Tkinter support
4. libtextworker[wx]: Same as libtextworker[tkinter], but for wxPython
5. libtextworker[all]: Install everything above

Note: For the application autocolor support, the support is OS-dependent:
* Windows 10 1607+
* macOS 10.14
* Linux/BSD with at least GTK3?

## Install

libtextworker is available on:
* [GitHub](https://github.com/lebao3105/libtextworker) and GitHub [releases](https://github.com/lebao3105/libtextworker/releases)
* [Pypi](https://pypi.org/project/libtextworker)
