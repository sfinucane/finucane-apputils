# -*- coding: utf-8 -*-
"""Python 2.6 and newer support compatibility layer.

Intended use: ``from compatibility import *``
"""
from future.builtins import (bytes, dict, int, list, object, range, str,
                             ascii, chr, hex, input, next, oct, open,
                             pow, round, super, filter, map, zip)

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

__enhanced__ = ['bytes', 'dict', 'int', 'list', 'object', 'range', 'str',
                 'ascii', 'chr', 'hex', 'input', 'next', 'oct', 'open',
                 'pow', 'round', 'super', 'filter', 'map', 'zip']


def make_compatible(namespace):
    namespace['future'] = __import__('future', globals=namespace, fromlist=[], level=0)
    enhanced_ = __import__('future.builtins', globals=namespace, fromlist=__enhanced__, level=0)
    for e in __enhanced__:
        namespace[e] = getattr(enhanced_, e)

    if 'unicode' not in namespace:
        namespace['unicode'] = namespace['str']

    namespace['__python_version__'] = __python_version__
