.. finucane-apputils documentation master file, created by
   sphinx-quickstart on Mon Jun  2 15:06:27 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Finucane-Apputils Documentation
===============================

:Release: |release|
:Date: |today|


Finucane Research application building framework and utilities for Python.

This framework has one, clear goal: to allow the rapid development of consistent, "standard" tools (using Python).
There are two key parts to this goal to keep in mind when either using or developing this framework: **rapid** and
**standard**. Remember: the standard part is more flexible than the rapid part. Take from that mantra what you wish.

For now, this project is focused on providing a package that will allow a command-line tool developer to worry less
about how their tool is packaged for command-line use, and more about the core functionality of the tool. By
providing a layer of abstraction between the developer and the underlying feature implementations which are common
to most, if not all, tools, we can not only ease the burden for the developer, but we can make the tools more
future-proof (as long as the core functionality of the tool doesn't break in ways not controlled by the abstraction).
This means that if the API for the underlying argument parsing library changes, ``finucane-apputils`` can be updated to
propagate that change to all of your tools at once.

Finucane-Apputils works with Python 3 (tested on ≥ 3.2), and Python 2 (≥ 2.6), with no transformations or 2to3,
thanks to the ``future`` package.

Please don't hesitate to report issues to our tracker_ on GitHub.

Getting Started
===============

1. **Install**

.. literalinclude:: pip_install.txt
   :linenos:

or download from PyPi_ and perform a manual installation.

2. **Try it out**

.. literalinclude:: simplest_example.py
   :language: python
   :linenos:

or try it out in an interactive session:

.. literalinclude:: simplest_interactive_example.txt
   :language: python
   :linenos:

Using Finucane-Apputils
=======================

.. include:: code.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Links
=====

* finucane-apputils on GitHub_
* finucane-apputils on PyPi_
* Wiki_
* Issue Tracker_

.. _GitHub: https://github.com/sfinucane/finucane-apputils
.. _PyPi: https://pypi.python.org/pypi/finucane-apputils
.. _wiki: https://github.com/sfinucane/finucane-apputils/wiki
.. _tracker: https://github.com/sfinucane/finucane-apputils/issues

License
=======
All Finucane-Apputils Python source code is licensed as follows::

    The MIT License (MIT)

    Copyright (c) 2014 Sean Anthony Finucane

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
