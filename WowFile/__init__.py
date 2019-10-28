#!/usr/bin/env python3

try:
    import BUILD_CONSTANTS
    version = BUILD_CONSTANTS.BUILD_VERSION
except ImportError:
    try:
        from ._version import version as __version__
    except ImportError:
        try:
            import git
            r = git.repo.Repo('./')
            __version__ = r.git.describe("--tags", "--dirty")
        except ImportError:
            __version__ = "?version unknown?"
            pass
    pass

from .wow import WowFile
from . import tkViewer

