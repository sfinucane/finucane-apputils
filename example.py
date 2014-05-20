#!/usr/bin/env python
"""
"""
import sys
from finucane.apputils import Application

__version__ = '0.1.0'

PROGRAM_DESCRIPTION = ''
PROGRAM_EPILOG = ''

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
                default_config_file=DEFAULT_CONFIG_FILE,
                stdout=sys.stdout,
                stderr=sys.stderr)

    app.run(message='Hello World!')
