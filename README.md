This directory contains makepy, a Python framework for generating Makefiles.

makepy allows you to define build rules and variables in Python and render
them to a Makefile. It provides a type-safe interface for constructing make
rules and includes standard library support for common build tasks.


Quick Start
-----------

Create a configure.py file that defines your build rules:

  from makepy import Context
  from std.cc import ccompile, CCompileArgs

  CONTEXT = Context()
  CC = CONTEXT.variable("CC", "gcc")
  CFLAGS = CONTEXT.variable("CFLAGS", "-Wall -Wextra")

  info = ccompile(
      CONTEXT,
      CCompileArgs(
          in_=["src/main.c"],
          out="src/main.o",
          cc=CC,
          cflags=CFLAGS,
          linking=False,
      ),
  )

  CONTEXT.add_default(info)

  with open("Makefile", "w") as f:
      CONTEXT.render(f)

Run the configuration script to generate the Makefile:

  python configure.py

Then build with make:

  make


Examples
--------

See the example directory for complete working examples.


Standard Library
----------------

The std directory contains reusable build rules:

  - std/cc.py: C compilation rules (ccompile, ccompile_many)
  - std/packaging.py: Archive and clean rules
  - std/bins.py: System binary detection utilities


License
-------

Copyright (C) 2026 Me lol.
