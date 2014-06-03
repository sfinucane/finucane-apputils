#!/usr/bin/env python
"""
.. module:: error
   :platform: All
   :synopsis: Write me.

.. moduleauthor:: Sean Anthony Finucane <s.finucane001@gmail.com>
"""


class ApputilsError(Exception):
    pass


class ArgumentParseError(ApputilsError):
    pass
