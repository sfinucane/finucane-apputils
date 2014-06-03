#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
  Examples can be given using either the ``Example`` or ``Examples``
  sections. Sections support any reStructuredText formatting, including
  literal blocks::

      $ python example_google.py

Section breaks are created by simply resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
  module_level_variable (int): Module level variables may be documented in
    either the ``Attributes`` section of the module docstring, or in an
    inline docstring immediately following the variable.

    Either form is acceptable, but the two should not be mixed. Choose
    one convention to document module level variables and be consistent
    with it.

.. _Google Python Style Guide:
   http://google-styleguide.googlecode.com/svn/trunk/pyguide.html

"""
# Python 2.6 and newer support
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import (
                bytes, dict, int, list, object, range, str,
                ascii, chr, hex, input, next, oct, open,
                pow, round, super,
                filter, map, zip)
try:
    unicode()
except NameError:
    unicode = str

import sys
__python_version__ = dict()
try:
    __python_version__['major'] = sys.version_info.major
except AttributeError:
    __python_version__['major'] = sys.version_info[0]
try:
    __python_version__['minor'] = sys.version_info.minor
except AttributeError:
    __python_version__['minor'] = sys.version_info[1]


__all__ = ("Namespace", "as_namespace")

from collections import Mapping, Sequence, defaultdict

from .error import ApputilsError


class NamespaceError(ApputilsError):
    pass


class NamespaceNotMutableError(NamespaceError):
    pass


class Namespace(object):
    """A dict subclass that exposes its items as attributes.

    Warning: Namespace instances do not have direct access to the
    dict methods.

    """

    def __init__(self, default_factory=None, data=None):
        if default_factory is None:
            default_factory = lambda: None
        if data is None:
            data = {}
        # using ``super`` (especially from ``future``) can be tricky in this case (so don't use it)!
        super_ = object
        super_.__init__(self)
        self.__dict__ = defaultdict(default_factory, data)

    def __dir__(self):
        return self.__dict__.dir()

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, sorted(dict(self.__dict__)))

    def __getattribute__(self, item):
        # using ``super`` (especially from ``future``) can be tricky in this case (so don't use it)!
        super_ = object
        if str(item).startswith('__'):
            return super_.__getattribute__(self, item)
        return super_.__getattribute__(self, '__dict__')[item]


class ImmutableNamespace(Namespace):
    """
    """
    def __setitem__(self, key, value):
        raise NamespaceNotMutableError('Cannot mutate non-mutable Namespace!')

    def __setattr__(self, name, value):
        if name in ['__dict__']:
            super().__setattr__('__dict__', value)
        else:
            raise NamespaceNotMutableError('Cannot mutate non-mutable Namespace!')

    def __delattr__(self, name):
        if name in ['__dict__']:
            self.__dict__ = None
        else:
            raise NamespaceNotMutableError('Cannot mutate non-mutable Namespace!')
