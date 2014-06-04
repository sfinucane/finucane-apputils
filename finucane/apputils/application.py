# -*- coding: utf-8 -*-
"""finucane.apputils.application

Provides the ``Application`` class. That is all this module is expected to do.

:copyright: (c) 2014 by Sean Anthony Finucane.
:license: MIT, see LICENSE for more details.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
# Python 2.6 and newer support
from __future__ import (absolute_import, division, print_function, unicode_literals)
from finucane.apputils.compatibility import make_yesterpy_compatible
make_yesterpy_compatible(globals())

import sys
import logging
import logging.handlers
import traceback
import inspect
from uuid import uuid4 as uuid

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

from .namespace import Namespace, ImmutableNamespace
from .errors import ApputilsParseError
from .args import BasicArgumentParser
from .log import LogAboveErrorFilter


def _make_safe_name(name):
    return "_".join(name.split())


def _make_option_name(name):
    return name.lower().replace('_', '-')


class ApplicationKernel(object):
    """Most generic, public abstract base.

    If you are an application developer, this is the most general application
    class, from which all other application classes inherit. When inheriting
    from this class, a developer must implement the ``_main`` method.

    Attributes:
        app_id: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """
    STDLOG_FSPEC = '[pid: %(process)d | log: %(name)s | level: %(levelname)s | time: %(asctime)s]\n\t>>> %(message)s'
    STDERR_FSPEC = STDLOG_FSPEC

    def __init__(self, name='', version='0.1.0', description='', epilogue='',
                 stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr,
                 stdlog=sys.stderr,
                 credits=None, organization=''):
        object.__init__(self)
        self.name = name

        self.app_debug_id = None
        self._stdlog_handler = None
        self._stderr_handler = None
        self._netlog_handler = None

        self._version = version
        self._full_name = '{n}, version {v}'.format(n=name, v=version)
        self._description = description
        self._epilogue = epilogue
        self._organization = organization
        self._credits = credits

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.stdlog = stdlog

        self.args = None
        self.config = None
        self.log = None
        self.arg_parser = None

        self.state = Namespace()

        # instance UUID:
        self._uuid = uuid()

    @property
    def version(self):
        return self._version

    @property
    def full_name(self):
        return self._full_name

    @property
    def description(self):
        return self._description

    @property
    def epilogue(self):
        return self._epilogue

    @property
    def organization(self):
        return self._organization

    @property
    def credits(self):
        return self._credits

    @property
    def uuid(self):
        return self._uuid

    @property
    def app_id(self):
        """A unique identifier string for the APPLICATION (not the instance)."""
        organization = self.organization.lower().strip().replace('.', '-').replace(' ', '_')
        name = self.name.lower().strip().replace('.', '-').replace(' ', '_')
        version = self.version.lower().strip().replace('.', '-').replace(' ', '_')
        return '{org}.{name}.{vers}'.format(org=organization, name=name, vers=version)

    @property
    def id_(self):
        """A unique identifier string for the application instance."""
        return "".join([self.app_id, '.', str(self.uuid)])

    def print(self, *args, **kwargs):
        """Print ``*args`` to ``self.stdout``, unless other out file given.

        Essentially, this is an alias for the built-in print function which
        prints to the calling instance's ``stdout`` by default.
        """
        if 'file' in kwargs:
            return print(*args, **kwargs)
        else:
            return print(*args, file=self.stdout, **kwargs)

    def _initialize(self):
        pass

    def _main(self, *args, **kwargs):
        raise NotImplementedError

    def _on_success(self):
        pass

    def _on_failure(self):
        pass

    def _finalize(self):
        pass

    def __call__(self, *args, **kwargs):
        """Alias for ``run`` method."""
        return self.run(*args, **kwargs)

    def exec_(self, *args, **kwargs):
        """Alias for ``run`` method."""
        return self.run(*args, **kwargs)

    def run(self, argv=[], *args, **kwargs):

        self.app_debug_id = '{c}.{f}'.format(c=str(self.__class__).strip().split("'")[1],
                                             f=inspect.currentframe().f_code.co_name)

        try:
            # logging facility
            self.log = logging.getLogger(self.app_id)

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
            parsed_args = {}
            try:
                parsed_args = self.arg_parser.parse_args(argv)
            except ApputilsParseError as e:
                self.log.critical(e)
                raise e

            # grab things that should NOT be left in the args container
            if hasattr(parsed_args, 'config'):
                self.config = parsed_args.config
                vars(parsed_args)['config'] = None

            else:
                self.config = ApplicationConfig(file_path=None)

            # all arguments in ``self.args`` must be a list! Make it so.
            for key, value in vars(parsed_args).items():
                if not isinstance(value, list):
                    setattr(parsed_args, key, [value])

            self.args = ImmutableNamespace(default_factory=lambda: [None],
                                           data=vars(parsed_args))

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

        except ApputilsParseError as e:
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


class Application(ApplicationKernel):
    """Public abstract base class for applications with "standard" features.

    If you are an application developer, this is the most general application
    class, from which all other application classes inherit. When inheriting
    from this class, a developer must implement the ``_main`` method.

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """
    def __init__(self, name='', version='0.1.0', description='', epilogue='',
                 default_config_file=None,
                 stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr,
                 stdlog=sys.stderr,
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
        self.epilog = epilogue
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
        self.arg_parser = BasicArgumentParser(default_config_file=default_config_file,
                                               prog=name,
                                               description=description,
                                               epilog=epilogue,
                                               fromfile_prefix_chars='@')
        self.arg_parser.add_argument(
            '--version', action='version', version='%(prog)s {vers}'.format(vers=self.version))

    @property
    def app_id(self):
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
        self.arg_parser.add_argument(
            safe_name, metavar=safe_name.upper(), type=type_, nargs=nargs,
            help=help_)

    def add_restricted_argument(self, name, choices, help_='', type_=str, nargs=1):
        safe_name = _make_safe_name(name)

        augmented_help = '{orig} (choices: {c})'.format(orig=help_,
                                                        c=str(choices).strip().replace('[', '').replace(']', ''))

        self.arg_parser.add_argument(
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
            self.arg_parser.add_argument(
                '-{f}'.format(f=unix_flag),
                '--{n}'.format(n=optname), dest=dest, action='append',
                default=[default], type=type_,
                help=help_)
        else:
            self.arg_parser.add_argument(
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
            self.arg_parser.add_argument(
                '-{f}'.format(f=unix_flag),
                '--{n}'.format(n=optname), dest=dest, action='append',
                choices=choices,
                default=default, type=type_,
                help=help_)
        else:
            self.arg_parser.add_argument(
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
            self.arg_parser.add_argument(
                '-{f}'.format(f=unix_flag),
                '--{n}'.format(n=optname), dest=dest, action='count',
                default=default,
                help=help_)
        else:
            self.arg_parser.add_argument(
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
            self.arg_parser.add_argument(
                '-{f}'.format(f=unix_flag),
                '--{n}'.format(n=optname), dest=dest, action=action,
                help=help_)
        else:
            self.arg_parser.add_argument(
                '--{n}'.format(n=optname), dest=dest, action=action,
                help=help_)

    def _initialize(self):
        pass

    def _main(self, *args, **kwargs):
        raise NotImplementedError

    def _on_success(self):
        pass

    def _on_failure(self):
        pass

    def _finalize(self):
        pass

    def exec_(self, *args, **kwargs):
        self.run(*args, **kwargs)

    def run(self, argv=[], *args, **kwargs):
        self.app_debug_id = '{c}.{f}'.format(c=str(self.__class__).strip().split("'")[1],
                                             f=inspect.currentframe().f_code.co_name)

        try:
            # logging facility
            self.log = logging.getLogger(self.app_id)

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
                parsed_args = self.arg_parser.parse_args(argv)
            except ApputilsParseError as e:
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

        except ApputilsParseError as e:
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


