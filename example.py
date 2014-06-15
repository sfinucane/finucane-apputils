# -*- coding: utf-8 -*-
"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

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
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from finucane.apputils.compatibility import upgrade_namespace
upgrade_namespace(globals())

import sys
import time
from finucane.apputils import Application

__version__ = '0.1.0'

PROGRAM_DESCRIPTION = 'An example application which showcases the Finucane Research apputils framework.'
PROGRAM_EPILOGUE = 'See http://www.github.com/sfinucane/finucane-apputils for more information.\nCopyright (c) 2014 Sean A. Finucane'
ORGANIZATION = 'Finucane Research'

DEFAULT_CONFIG_FILE = 'app.ini'


class MyApp(Application):
    def __init__(self, name='', stdout=sys.stdout, stderr=sys.stderr,
                 stdlog=sys.stderr):
        super().__init__(name=name,
                         stdout=stdout, stderr=stderr, stdlog=stdlog,
                         description=PROGRAM_DESCRIPTION,
                         epilogue=PROGRAM_EPILOGUE,
                         organization=ORGANIZATION,
                         default_config_file=DEFAULT_CONFIG_FILE)

        self.arg_parser.add_argument(
            'intro',
            help_='the message to give to the user (e.g., "Welcome aboard!")')

        self.arg_parser.add_restricted_argument(
            'free', choices=['speech', 'beer'],
            help_='choose wisely, but don\'t stall man')

        self.arg_parser.add_option(
            'username', unix_flag='u', default='John Doe',
            help_="the username to use. repeatable. in this case only the final name specified will be used")

        self.arg_parser.add_counted_option(
            'awesomeness level', unix_flag='a',
            help_='Adds awesomeness (the more, the greater the awesome level).')

        self.arg_parser.add_restricted_option(
            'flavor', choices=['chocolate', 'vanilla', 'strawberry'],
            help_='your favorite flavor')

        self.arg_parser.add_switch(
            'show intro', unix_flag='s',
            help_='if set, the welcome message is shown')

    def _initialization(self):
        if self.state.exec_time is not None:
            self.print('Previous execution timestamp:', self.state.exec_time)
        self.state.exec_time = time.time()

    def _main(self, message):
        if self.args.show_intro[-1]:
            self.print('{usr}: {m}'.format(usr=self.args.username[-1], m=self.args.intro[-1]))
        self.print('{usr}: {m}'.format(usr=self.args.username[-1], m=message))
        self.print('{usr}: You are awesome, {a} times over!'.format(usr=self.args.username[-1],
                                                                    a=self.args.awesomeness_level[-1]))
        if self.args.flavor:
            self.print('{usr}: You chose the {f} flavor!'.format(usr=self.args.username[-1],
                                                                 f=self.args.flavor[-1]))
        self.print(self.state.nonexistant)

    def _on_success(self):
        pass

    def _on_failure(self):
        pass

    def _finalization(self):
        self.print('Goodbye {usr}!'.format(usr=self.args.username[-1]))


if __name__ == '__main__':
    app = MyApp(name=sys.argv[0], stdout=sys.stdout, stderr=sys.stderr)

    print('Running:', app.app_id, 'with args:', sys.argv[1:])
    app.run(argv=sys.argv[1:], message="It's very nice to meet you!")
    app.run(argv=sys.argv[1:], message='Hello again!')

    import pickle
    pickled_app = pickle.dumps(app)

    rehydrated = pickle.loads(pickled_app)
    rehydrated(argv=sys.argv[1:], message='I was pickled, now I am not!')
