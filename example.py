#!/usr/bin/env python
"""
"""
import sys
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
    app.add_option('username', default='John Doe',
                   help_="the username to use. repeatable. in this case only the final name specified will be used")

    print('Running:', app.id_, 'with args:', sys.argv[1:])
    app.run(message="It's very nice to meet you!")
