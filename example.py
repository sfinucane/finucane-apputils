#!/usr/bin/env python
"""
"""
import sys
from finucane.apputils import Application

__version__ = '0.1.0'

PROGRAM_DESCRIPTION = 'An example application which showcases the Finucane Research apputils framework.'
PROGRAM_EPILOG = 'See http://www.github.com/sfinucane/finucane-apputils for more information.'
ORGANIZATION = 'Finucane Research'

DEFAULT_CONFIG_FILE = 'app.ini'


class MyApp(Application):
    def _initialize(self):
        self.state.username = 'John Doe'

    def _main(self, message=''):
        self.print('{usr}: {m}'.format(usr=self.state.username, m=message))
        self.print(self.state.nonexistant)

    def _on_success(self):
        pass

    def _on_failure(self):
        pass

    def _finalize(self):
        self.print('Goodbye {usr}!'.format(usr=self.state.username))


if __name__ == '__main__':
    app = MyApp(name=sys.argv[0],
                description=PROGRAM_DESCRIPTION,
                epilog=PROGRAM_EPILOG,
                organization=ORGANIZATION,
                default_config_file=DEFAULT_CONFIG_FILE,
                stdout=sys.stdout,
                stderr=sys.stderr)

    print('Running:', app.id_, 'with args:', sys.argv[1:])
    app.run(message='Hello World!')
