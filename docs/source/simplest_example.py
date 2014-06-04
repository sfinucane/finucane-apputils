"""simplest_example.py"""
from finucane.apputils import Application


class MyApplication(Application):

    def _main(self, message=None):
        self.print(message)


if __name__ == '__main__':
    import sys
    app = MyApplication()
    app.run(argv=sys.argv[1:], message="Hello World!")  # alternative: app.exec_(...)
