#!/usr/bin/env python
"""
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

import time
from finucane.apputils import Application

__version__ = '0.1.0'

PROGRAM_DESCRIPTION = 'An example application which showcases the Finucane Research apputils framework.'
PROGRAM_EPILOG = 'See http://www.github.com/sfinucane/finucane-apputils for more information.'
ORGANIZATION = 'Finucane Research'

DEFAULT_CONFIG_FILE = 'app.ini'


class MyApp(Application):
    def _initialize(self):
        if self.state.exec_time is not None:
            self.print('Previous execution timestamp:', self.state.exec_time)
        self.state.exec_time = time.time()

    def _main(self, message=''):
        self.print('{usr}: {m}'.format(usr=self.args.username[-1], m=self.args.intro[-1]))
        self.print('{usr}: {m}'.format(usr=self.args.username[-1], m=message))
        self.print(self.state.nonexistant)

    def _on_success(self):
        pass

    def _on_failure(self):
        pass

    def _finalize(self):
        self.print('Goodbye {usr}!'.format(usr=self.args.username[-1]))


if __name__ == '__main__':
    app = MyApp(name=sys.argv[0],
                description=PROGRAM_DESCRIPTION,
                epilog=PROGRAM_EPILOG,
                organization=ORGANIZATION,
                default_config_file=DEFAULT_CONFIG_FILE,
                stdout=sys.stdout,
                stderr=sys.stderr)

    app.add_argument('intro', help_='the message to give to the user (e.g., "Welcome aboard!")')
    app.add_option('username', unix_flag='u', default='John Doe',
                   help_="the username to use. repeatable. in this case only the final name specified will be used")
    app.add_counted_option('awesomeness', unix_flag='a',
                           help_='Adds awesomeness (the more, the greater the awesome level).')


    print('Running:', app.id_, 'with args:', sys.argv[1:])
    app.run(args=sys.argv[1:], message="It's very nice to meet you!")
    app.run(args=sys.argv[1:], message='Hello again!')
