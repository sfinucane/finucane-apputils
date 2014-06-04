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
from __future__ import (absolute_import, division, print_function, unicode_literals)
from finucane.apputils.compatibility import make_yesterpy_compatible
make_yesterpy_compatible(globals())

import sys
import time
from finucane.apputils import Application

__version__ = '0.1.0'

PROGRAM_DESCRIPTION = 'An example application which showcases the Finucane Research apputils framework.'
PROGRAM_EPILOG = 'See http://www.github.com/sfinucane/finucane-apputils for more information.\nCopyright (c) 2014 Sean A. Finucane'
ORGANIZATION = 'Finucane Research'

DEFAULT_CONFIG_FILE = 'app.ini'


class MyApp(Application):
    def _initialize(self):
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

    app.add_argument('intro',
                     help_='the message to give to the user (e.g., "Welcome aboard!")')
    app.add_restricted_argument('free', choices=['speech', 'beer'],
                                help_='choose wisely, but don\'t stall man')
    app.add_option('username', unix_flag='u', default='John Doe',
                   help_="the username to use. repeatable. in this case only the final name specified will be used")
    app.add_counted_option('awesomeness level', unix_flag='a',
                           help_='Adds awesomeness (the more, the greater the awesome level).')
    app.add_restricted_option('flavor', choices=['chocolate', 'vanilla', 'strawberry'],
                              help_='your favorite flavor')
    app.add_switch('show intro', unix_flag='s',
                   help_='if set, the welcome message is shown')


    print('Running:', app.id_, 'with args:', sys.argv[1:])
    app.run(argv=sys.argv[1:], message="It's very nice to meet you!")
    app.run(argv=sys.argv[1:], message='Hello again!')
