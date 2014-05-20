#!/usr/bin/env python
"""
"""
import sys
import time
import argparse
import configparser
import logging
import logging.handlers
import traceback
import inspect
from io import StringIO
from xml.sax import saxutils
from collections import defaultdict

from .dictattraccessor import DictAttrAccessor


class ApplicationConfig(configparser.ConfigParser):
    """
    """
    def __init__(self, file_path):
        configparser.ConfigParser.__init__(self)
        self._file_path = file_path
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


class BasicArgumentParser(argparse.ArgumentParser):
    """
    """
    def __init__(self, default_config_file=None, **kwargs):
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                          help='output additional information to stderr (more v\'s mean more output, 4 is maximal)')
        if default_config_file:
            self.add_argument('--config', dest='config', action='store',
                              default=default_config_file, type=ApplicationConfig,
                              help='path to the configuration file.')
        self.add_argument('--netlog-host', dest='netlog_host', action='store',
                          default=None, type=str,
                          help='hostname of the socket server to which log events will be sent (e.g., "localhost")')
        self.add_argument('--netlog-port', dest='netlog_port', action='store',
                          default=logging.handlers.DEFAULT_TCP_LOGGING_PORT, type=int,
                          help='port number of the socket logging handler to which log events will be sent')


STD_LOG_FSPEC = '[pid: %(process)d | log: %(name)s | level: %(levelname)s | time: %(asctime)s]\n>>> %(message)s\n'

def setup_logger(logger_name=None, outfile=sys.stdout,
                 format_spec=STD_LOG_FSPEC,
                 log_level=logging.INFO,
                 netlog_host='localhost',
                 netlog_port=logging.handlers.DEFAULT_TCP_LOGGING_PORT):
    log = logging.getLogger(logger_name)

    log_handler = logging.StreamHandler(outfile)
    log_formatter = logging.Formatter(format_spec)
    log_handler.setFormatter(log_formatter)
    log.addHandler(log_handler)

    if netlog_host and netlog_port:
        socket_handler = logging.handlers.SocketHandler(netlog_host, netlog_port)
        log.addHandler(socket_handler)

    log.setLevel(log_level)

    return log


class Application(object):
    """
    """
    def __init__(self, name='', version='0.1.0', description='', epilog='', default_config_file=None,
                 stdout=sys.stdout, stderr=sys.stderr, credits=None, organization=''):
        object.__init__(self)
        self.name = name
        self.version = version
        self.full_name = '{n}, version {v}'.format(n=name, v=version)
        self.description = description
        self.epilog = epilog
        self.organization = organization
        self.credits = credits
        self.stdout = stdout
        self.stderr = stderr

        self.args = None
        self.config = None
        self.log = None

        self.state = DictAttrAccessor(dict_=defaultdict(type(None)))

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
        safe_name = "".join(name.split())
        self._arg_parser.add_argument(
            safe_name, metavar=safe_name.upper(), type=type_, nargs=nargs,
            help=help_)

    def add_option(self, name, default=None, help_='',  type_=str, dest=None):
        if default is None:
            default = type_()

        safe_name = "".join(name.split())
        if dest is None:
            dest = safe_name

        optname = safe_name.lower().replace('_', '-')
        self._arg_parser.add_argument(
            '--{n}'.format(n=optname), dest=dest, action='append',
            default=[default], type=type_,
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

    def run(self, args=sys.argv[1:], **kwargs):
        self.app_debug_id = '{c}.{f}'.format(c=str(self.__class__).strip().split("'")[1],
                                             f=inspect.currentframe().f_code.co_name)

        # initialize the application based on given arguments.
        self.args = self._arg_parser.parse_args(args)
        self.config = self.args.config if hasattr(self.args, 'config') else None
        assert hasattr(self.args, 'verbose')
        # logger
        logging_level = logging.FATAL
        if self.args.verbose < 1:
            logging_level = logging.CRITICAL
        elif self.args.verbose == 1:
            logging_level = logging.ERROR
        elif self.args.verbose == 2:
            logging_level = logging.WARNING
        elif self.args.verbose == 3:
            logging_level = logging.INFO
        elif self.args.verbose > 3:
            logging_level = logging.DEBUG

        self.log = setup_logger(logger_name=self.name, outfile=self.stderr, log_level=logging_level,
                                netlog_host=self.args.netlog_host, netlog_port=self.args.netlog_port)

        assert self.log is not None
        assert hasattr(self.log, 'critical')
        assert hasattr(self.log, 'debug')
        assert hasattr(self.log, 'info')

        # ready to roll!
        self.log.debug('Entering {app_id}'.format(app_id=self.app_debug_id))
        try:
            assert self.config is not None
            assert self.args is not None

            self.log.debug('config = {0!s}'.format(self.config.as_dict()))
            self.log.debug('args = {0!s}'.format(vars(self.args)))
            self.log.debug('log_name = "{0!s}"'.format(self.log.name))

            self.log.info('Executing initialization hook.')
            self._initialize()
            self.log.info('Executing primary function.')
            self._main(**kwargs)
            self.log.info('Primary function exited cleanly. Executing success hook.')
            self._on_success()

        except Exception as e:
            self.log.info('An exception occurred! Executing failure hook.')
            self._on_failure()
            with StringIO() as err_msg:
                print(e, file=err_msg)
                traceback.print_exc(file=err_msg)
                self.log.critical(err_msg.getvalue())
        finally:
            self.log.info('Executing finalization hook.')
            self._finalize()
            self.log.debug('Exiting {app_id}'.format(app_id=self.app_debug_id))
