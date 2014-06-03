# -*- coding: utf-8 -*-
"""apputils.errors

Provides exceptions used by the Apputils modules.  Note that Apputils
modules may raise standard exceptions.

This module is safe to use in "from ... import *" mode; it only exports
symbols whose names start with "Apputils" and end with "Error".
"""


class ApputilsError (Exception):
    """The root of all Apputils evil."""
    pass


class ApputilsParseError(ApputilsError):
    """Raised by any Apputils parser when a parse goes off a cliff."""
    pass
