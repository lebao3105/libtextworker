"""
@package libtextworker.versioning
@brief Utilities for version control management.
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023-2024 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

import importlib
import packaging.version

from . import general

"""
Projects called by functions under libtextworker.versioning.
"""
Requested = {}


def parse_version(project: str) -> packaging.version.Version:
    """
    Tries to import a project then parse its version with the ```packaging.version``` module.
    Parsed projects are stored in Requested (list).
    Returns None on error.

    @see is_development_version
    @see is_development_from_project
    @see require
    @see require_exact
    @see require_lower
    @see Requested
    """

    global Requested
    try:
        module = importlib.import_module(project)
    except:
        Requested[project] = None

    if project not in Requested:
        if not module.__version__:
            Requested[project] = None
            raise general.libTewException(f"{project} does not have __version__ attribute!")
        Requested[project] = packaging.version.parse(module.__version__)

    return Requested[project]


def is_development_version(version: str):
    """
    Parse and check if the specified version is a prerelease.
    @see is_development_version_from_project
    """
    return packaging.version.parse(version).is_prerelease


def is_development_version_from_project(project: str):
    """
    Like is_development_version(), but read the project's current version instead.
    @see is_development_version
    """
    return parse_version(project).is_prerelease


def require(project: str, target_version: str):
    """
    Ensures the correct versions of a project are available.
    @param project (str): Target project name
    @param target_version (str): Target project version
    """
    currver = parse_version(project)
    target = packaging.version.parse(target_version)

    if currver < target:
        raise general.libTewException(
            "Project %(project)s must have version >=%(target_version)s"
        )


def require_exact(project: str, target_version: str):
    """
    Ensures the correct version of a project IS available.
    @param project (str): Target project name
    @param target_version (str): Target project version
    """
    currver = parse_version(project)
    target = packaging.version.parse(target_version)

    if currver != target:
        raise general.libTewException(
            "Project %(project)s version %(target_version)s is not available"
        )


def require_lower(project: str, target_version: str):
    """
    Ensures the project version is LOWER than the requested one.
    @param project (str): Target project name
    @param target_version (str): Target project version
    """
    currver = parse_version(project)
    target = packaging.version.parse(target_version)

    if currver >= target:
        raise general.libTewException(
            "Project %(project)s version %(target_version)s is not available"
        )
