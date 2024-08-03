# Installing libtextworker

The latest version of this library is 0.1.4.

You will need:

* Python 3 or higher with pip installed - get it from [python.org](https://python.org)
* Basic Python programming knowledge - this is not really a project for beginners

## Available packages

With the 0.1.3 release, we have these following packages:

1. libtextworker: The smallest package, ideal for command-line projects
2. libtextworker[`autocolor`]: Autocolor (depends on the system's color) support for GUI apps
3. libtextworker[`tkinter`]: Install requirements for Tkinter support
4. libtextworker[`wx`]: Same as libtextworker[`tkinter`], but for wxPython
5. libtextworker[`all`]: Everything above

Note: For the application autocolor support, the support is OS-dependent:

* Windows 10 1607+
* macOS 10.14+
* Linux/BSD with at least GTK3?

'Auto color' means getting the current OS color scheme (dark/light) and eventually apply that to the interface.

## Install

libtextworker is available on:
* [GitHub](https://github.com/lebao3105/libtextworker) (mirror)
* [Official Gitlab page](https://gitlab.com/textworker/legacy-python/libtextworker)
* [Pypi](https://pypi.org/project/libtextworker)

Install from source:

```bash
$ pip install .
$ # Or
$ pip install .[things here as you wish]
$ # Or
$ poetry install .[things here too]
```

From Pypi:

```bash
$ pip install libtextworker[blahblah]
```

<div class="section_buttons">

| Previous                   |                       Next |
|:---------------------------|---------------------------:|
| [Home](../index.md)                  | [What to pick?](gettheright.md) |

</div>