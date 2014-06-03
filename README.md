finucane-apputils
=================

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

See LICENSE for license information.
See NOTICE for copyright notice.
