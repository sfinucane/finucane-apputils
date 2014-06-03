# -*- coding: utf-8 -*-
"""
"""
# Python 2.6 and newer support
from __future__ import (absolute_import, division, print_function, unicode_literals)
from finucane.apputils.compatibility import make_compatible
make_compatible(globals())

try:
    import configparser  # Python 3.x
except ImportError:
    import ConfigParser as configparser  # Python 2.x


class ApplicationConfig(configparser.ConfigParser):
    """ """
    def __init__(self, file_path):
        configparser.ConfigParser.__init__(self)
        self._file_path = file_path
        if file_path is not None:
            self.read(file_path)

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

    def __str__(self):
        return 'ApplicationConfig("{path}")'.format(path=self._file_path)

    def __repr__(self):
        return self.__str__()
