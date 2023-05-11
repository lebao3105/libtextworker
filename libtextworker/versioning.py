import importlib
import packaging.version

from . import general

"""
Projects called by functions under libtextworker.versioning.
"""
Requested = {}


def parse_version(project: str):
    """
    Try to import a project then parse its version with the ```packaging.version``` module.
    Parsed projects are stored in Requested (list).
    @see is_development_version
    @see is_development_from_project
    @see require
    @see require_exact
    @see require_lower
    @see Requested
    """
    global Requested
    module = importlib.import_module(project)

    if project not in Requested:
        if not module.__version__:
            raise general.libTewException(
                "%(project)s does not have __version__ attribute!"
            )
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
            "Project %(project)s not available for version %(target_version)"
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
            "Project %(project)s not available for version %(target_version)"
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
            "Project %(project)s not available for version %(target_version)"
        )
