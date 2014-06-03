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

import argparse  # included in Python >2.7, but not 2.6

try:
    import configparser  # Python 3.x
except ImportError:
    import ConfigParser as configparser  # Python 2.x

import logging
import logging.handlers
import traceback
import inspect

if __python_version__['major'] > 2:
    from io import StringIO
else:
    from StringIO import StringIO as StringIO2x
    class StringIO(StringIO2x):
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

if __python_version__['major'] > 2:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

#from .dictattraccessor import DictAttrAccessor
from .namespace import Namespace, ImmutableNamespace
from .error import ArgumentParseError


class ApplicationConfig(configparser.ConfigParser):
    """
    """
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


def NetloggerAddressParse(url, *args, **kwargs):
    """Fetches rows from a Bigtable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by big_table.  Silly things may happen if
    other_silly_variable is not None.

    Args:
        big_table: An open Bigtable Table instance.
        keys: A sequence of strings representing the key of each table row
            to fetch.
        other_silly_variable: Another optional variable, that has a much
            longer name than the other args, and which does nothing.

    Returns:
        A dict mapping keys to the corresponding table row data
        fetched. Each row is represented as a tuple of strings. For
        example:

        {'Serak': ('Rigel VII', 'Preparer'),
         'Zim': ('Irk', 'Invader'),
         'Lrrr': ('Omicron Persei 8', 'Emperor')}

        If a key from the keys argument is missing from the dictionary,
        then that row was not found in the table.

    Raises:
        IOError: An error occurred accessing the bigtable.Table object.
    """
    s_url = str(url)
    first_pass = urlparse(s_url)
    # first pass:
    if first_pass.hostname and first_pass.port:
        return first_pass
    # second pass:
    if not s_url.startswith('//'):
        s_url = "".join(["//", s_url])
    second_pass = urlparse(s_url, *args, **kwargs)
    # sanity check:
    if second_pass.hostname and second_pass.port:
        return second_pass
    # exhausted!
    raise ArgumentParseError('Cannot determine hostname/port for given netlogger string: "{url}"'.format(url=url))


class BasicArgumentParser(argparse.ArgumentParser):
    """Summary of class here.

    Longer class information....
    Longer class information....

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """
    def __init__(self, default_config_file=None, **kwargs):
        """ """
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.add_argument('-v', '--verbose', dest='verbosity', action='count', default=0,
                          help='output additional information to stderr (more v\'s mean more output, 4 is maximal)')
        # Only enable the config option is the default config is not set to None.
        if default_config_file is not None:
            self.add_argument('--config', dest='config', action='store',
                              default=default_config_file, type=ApplicationConfig,
                              help='path to the configuration file.')
        self.add_argument('--netlogger', dest='netlogger_url', action='store',
                          default=None, type=NetloggerAddressParse, nargs='*',
                          help='URL(s) of the socket server(s) to which log events will be sent (e.g., "localhost:9020")')


class LogAboveErrorFilter(logging.Filter):
    """
    """
    def __init__(self):
        logging.Filter.__init__(self)

    def filter(self, record):
        # CRITICAL = 50
        # ERROR = 40
        # WARNING = 30
        # INFO = 20
        # DEBUG = 10
        # NOTSET = 0
        if record.levelno < logging.ERROR:
            return 1
        else:
            return 0


def _make_safe_name(name):
    return "_".join(name.split())


def _make_option_name(name):
    return name.lower().replace('_', '-')


class Application(object):
    """
    """
    STDLOG_FSPEC = '[pid: %(process)d | log: %(name)s | level: %(levelname)s | time: %(asctime)s]\n\t>>> %(message)s'
    STDERR_FSPEC = STDLOG_FSPEC

    def __init__(self, name='', version='0.1.0', description='', epilog='', default_config_file=None,
                 stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, stdlog=sys.stderr,
                 credits=None, organization=''):
        object.__init__(self)
        self.name = name

        self.app_debug_id = None
        self._stdlog_handler = None
        self._stderr_handler = None
        self._netlog_handler = None

        self.version = version
        self.full_name = '{n}, version {v}'.format(n=name, v=version)
        self.description = description
        self.epilog = epilog
        self.organization = organization
        self.credits = credits

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.stdlog = stdlog

        self.args = None
        self.config = None
        self.log = None

        self.state = Namespace()

        # argument parser
        self._arg_parser = BasicArgumentParser(default_config_file=default_config_file,
                                               prog=name,
                                               description=description,
                                               epilog=epilog,
                                               formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                               fromfile_prefix_chars='@')
        self._arg_parser.add_argument(
            '--version', action='version', version='%(prog)s {vers}'.format(vers=self.version))

    @property
    def id_(self):
        organization = self.organization.lower().strip().replace('.', '-').replace(' ', '_')
        name = self.name.lower().strip().replace('.', '-').replace(' ', '_')
        version = self.version.lower().strip().replace('.', '-').replace(' ', '_')
        return '{org}.{name}.{vers}'.format(org=organization, name=name, vers=version)

    def print(self, *args, **kwargs):
        if 'file' in kwargs:
            return print(*args, **kwargs)
        else:
            return print(*args, file=self.stdout, **kwargs)

    def add_argument(self, name, help_='', type_=str, nargs=1):
        safe_name = _make_safe_name(name)
        self._arg_parser.add_argument(
            safe_name, metavar=safe_name.upper(), type=type_, nargs=nargs,
            help=help_)

    def add_restricted_argument(self, name, choices, help_='', type_=str, nargs=1):
        safe_name = _make_safe_name(name)

        augmented_help = '{orig} (choices: {c})'.format(orig=help_,
                                                        c=str(choices).strip().replace('[', '').replace(']', ''))

        self._arg_parser.add_argument(
            safe_name, metavar=safe_name.upper(), type=type_, nargs=nargs,
            choices=choices,
            help=augmented_help)

    def add_option(self, name, unix_flag=None, default=None, help_='',  type_=str, dest=None):
        if default is None:
            default = type_()

        safe_name = _make_safe_name(name)
        if dest is None:
            dest = safe_name

        optname = _make_option_name(safe_name)
        if unix_flag is not None:
            self._arg_parser.add_argument(
                '-{f}'.format(f=unix_flag),
                '--{n}'.format(n=optname), dest=dest, action='append',
                default=[default], type=type_,
                help=help_)
        else:
            self._arg_parser.add_argument(
                '--{n}'.format(n=optname), dest=dest, action='append',
                default=[default], type=type_,
                help=help_)

    def add_restricted_option(self, name, choices, unix_flag=None, default=None, help_='', type_=str, dest=None):
        if default is None:
            default = choices[0]

        safe_name = _make_safe_name(name)
        if dest is None:
            dest = safe_name

        optname = _make_option_name(safe_name)
        if unix_flag is not None:
            self._arg_parser.add_argument(
                '-{f}'.format(f=unix_flag),
                '--{n}'.format(n=optname), dest=dest, action='append',
                choices=choices,
                default=default, type=type_,
                help=help_)
        else:
            self._arg_parser.add_argument(
                '--{n}'.format(n=optname), dest=dest, action='append',
                choices=choices,
                default=default, type=type_,
                help=help_)

    def add_counted_option(self, name, unix_flag=None, default=None, help_='', dest=None):
        if default is None:
            default = 0

        safe_name = _make_safe_name(name)
        if dest is None:
            dest = safe_name

        optname = _make_option_name(safe_name)
        if unix_flag is not None:
            self._arg_parser.add_argument(
                '-{f}'.format(f=unix_flag),
                '--{n}'.format(n=optname), dest=dest, action='count',
                default=default,
                help=help_)
        else:
            self._arg_parser.add_argument(
                '--{n}'.format(n=optname), dest=dest, action='count',
                default=default,
                help=help_)

    def add_switch(self, name, unix_flag=None, default=None, help_='', dest=None):
        action = 'store_true'
        if default:
            action = 'store_false'

        safe_name = _make_safe_name(name)
        if dest is None:
            dest = safe_name

        optname = _make_option_name(safe_name)
        if unix_flag is not None:
            self._arg_parser.add_argument(
                '-{f}'.format(f=unix_flag),
                '--{n}'.format(n=optname), dest=dest, action=action,
                help=help_)
        else:
            self._arg_parser.add_argument(
                '--{n}'.format(n=optname), dest=dest, action=action,
                help=help_)

    def _initialize(self):
        pass

    def _main(self, *args, **kwargs):
        pass

    def _on_success(self):
        pass

    def _on_failure(self):
        pass

    def _finalize(self):
        pass

    def exec_(self, *args, **kwargs):
        self.run(*args, **kwargs)

    def run(self, args=[], **kwargs):
        self.app_debug_id = '{c}.{f}'.format(c=str(self.__class__).strip().split("'")[1],
                                             f=inspect.currentframe().f_code.co_name)

        try:
            # logging facility
            self.log = logging.getLogger(self.id_)

            assert self.log is not None
            assert hasattr(self.log, 'critical')
            assert hasattr(self.log, 'error')
            assert hasattr(self.log, 'warning')
            assert hasattr(self.log, 'info')
            assert hasattr(self.log, 'debug')

            if self.stdlog is not None:
                # events with a level above that of ERROR
                self._stdlog_handler = logging.StreamHandler(self.stdlog)
                stdlog_formatter = logging.Formatter(self.STDLOG_FSPEC)
                self._stdlog_handler.setFormatter(stdlog_formatter)
                self._stdlog_handler.addFilter(LogAboveErrorFilter())
                self.log.addHandler(self._stdlog_handler)

            if self.stderr is not None:
                # events with a level of ERROR and below
                self._stderr_handler = logging.StreamHandler(self.stderr)
                stderr_formatter = logging.Formatter(self.STDERR_FSPEC)
                self._stderr_handler.setFormatter(stderr_formatter)
                self._stderr_handler.setLevel(logging.ERROR)
                self.log.addHandler(self._stderr_handler)

            # default logging level before full init is CRITICAL
            self.log.setLevel(logging.CRITICAL)

            # initialize the application based on given arguments.
            try:
                parsed_args = self._arg_parser.parse_args(args)
            except ArgumentParseError as e:
                self.log.critical(e)
                raise e

            # grab things that should NOT be left in the args container
            self.config = parsed_args.config if hasattr(parsed_args, 'config') else ApplicationConfig(file_path=None)
            parsed_args.config = None

            # all arguments in ``self.args`` must be a list! Make it so.
            for key, value in vars(parsed_args).items():
                if not isinstance(value, list):
                    setattr(parsed_args, key, [value])

            self.args = ImmutableNamespace(default_factory=lambda: [None], data=vars(parsed_args))

            # logging configuration details
            assert hasattr(self.args, 'verbosity')

            logging_level = logging.CRITICAL
            if self.args.verbosity[-1] == 1:
                logging_level = logging.ERROR
            elif self.args.verbosity[-1] == 2:
                logging_level = logging.WARNING
            elif self.args.verbosity[-1] == 3:
                logging_level = logging.INFO
            elif self.args.verbosity[-1] > 3:
                logging_level = logging.DEBUG

            self.log.setLevel(logging_level)

            self._netlog_handler = []
            addresses = []
            for url in self.args.netlogger_url:
                if url is not None:
                    addresses.append({'host': url.hostname, 'port': url.port})

            for address in addresses:
                if address['host'] is not None and address['port'] is not None:
                    # a network capable logging facility (remote possibilities, etc.)
                    self._netlog_handler.append(logging.handlers.SocketHandler(address['host'], address['port']))
                    self.log.addHandler(self._netlog_handler[-1])

            self.log.debug('Preparing {app_id} environment.'.format(app_id=self.app_debug_id))

            # ready to roll!
            self.log.debug('Entering {app_id}'.format(app_id=self.app_debug_id))
            try:
                assert self.config is not None
                assert self.args is not None

                self.log.debug('config = {0!s}'.format(self.config.as_dict()))
                self.log.debug('args = {0!s}'.format(vars(self.args)))
                self.log.debug('log_name = "{0!s}"'.format(self.log.name))

                self.log.debug('Executing initialization hook.')
                self._initialize()
                self.log.debug('Executing primary function.')
                self._main(**kwargs)
                self.log.debug('Primary function exited cleanly. Executing success hook.')

            except Exception as e:
                self.log.critical('An exception occurred! Executing failure hook.')
                self._on_failure()
                with StringIO() as err_msg:
                    print(e, file=err_msg)
                    traceback.print_exc(file=err_msg)
                    self.log.critical(err_msg.getvalue())
            else:
                self.log.debug('Executing success hook.')
                self._on_success()
            finally:
                self.log.debug('Executing finalization hook.')
                self._finalize()
                self.log.debug('Exiting {app_id}'.format(app_id=self.app_debug_id))

        except ArgumentParseError as e:
            pass

        finally:
            # tear-down the logging facility
            if hasattr(self, '_stdlog_handler') and self._stdlog_handler is not None:
                self.log.removeHandler(self._stdlog_handler)

            if hasattr(self, '_stderr_handler') and self._stderr_handler is not None:
                self.log.removeHandler(self._stderr_handler)

            if hasattr(self, '_netlog_handler') and self._netlog_handler is not None:
                if isinstance(self._netlog_handler, list):
                    for handler in self._netlog_handler:
                        self.log.removeHandler(handler)
                else:
                    self.log.removeHandler(self._netlog_handler)
                self._netlog_handler = None


