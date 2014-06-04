# -*- coding: utf-8 -*-
"""finucane.apputils.args

Provides customized application argument(s) facilities and utilities. If a
customized or enhanced application argument(s) ability is needed, this is
where it should exist.

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

import argparse  # included in Python >2.7, but not 2.6


def NetloggerAddressParse(url, *args, **kwargs):
    """Fetches rows from a Bigtable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by big_table.  Silly things may happen if
    other_silly_variable is not None.

    Args:
        url: An open Bigtable Table instance.

    Returns:


    Raises:
        ApputilsParseError
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
    raise ApputilsParseError('Cannot determine hostname/port for given netlogger string: "{url}"'.format(url=url))


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

