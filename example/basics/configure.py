from makepy import (
    Context,
    expand,
)
from std.cc import ccompile, CCompileArgs
from std.packaging import archive, ArchiveArgs, clean, CleanArgs
from std.bins import get_rm

from pathlib import Path

PARENT_DIR = Path(__file__).parent
MAKEFILE = PARENT_DIR / "Makefile"

CONTEXT = Context()

ROOT_DIR = CONTEXT.variable("ROOT_DIR", str(PARENT_DIR))
SRC_DIR = CONTEXT.variable("SRC_DIR", expand([ROOT_DIR, "src"], delim="/"))
INCLUDE_DIR = CONTEXT.variable("LIB_INCLUDE", expand([ROOT_DIR, "includes"], delim="/"))

CC = CONTEXT.variable("CC", "gcc")
CFLAGS = CONTEXT.variable("CFLAGS", "-Wall -Wextra -Werror")

AR = CONTEXT.variable("AR", "ar")
ARFLAGS = CONTEXT.variable("ARFLAGS", "rcs")

RMFLAGS = CONTEXT.variable("RMFLAGS", "-rf")


if __name__ == "__main__":
    LIB_SOURCE = expand([SRC_DIR, "lib.c"], delim="/")
    LIB_OUT = expand([SRC_DIR, "lib.o"], delim="/")
    LIB_AR = expand([SRC_DIR, "lib.a"], delim="/")

    cflags = expand([CFLAGS, "-I", INCLUDE_DIR], delim=" ")

    lib_objs = ccompile(
        CONTEXT,
        CCompileArgs(
            in_=[LIB_SOURCE],
            out=LIB_OUT,
            cc=CC,
            cflags=cflags,
            linking=False,
        ),
    )

    lib_archive = archive(
        CONTEXT,
        ArchiveArgs(
            in_=lib_objs.files,
            out=LIB_AR,
            ar=AR,
            arflags=ARFLAGS,
        ),
    )

    BIN_SOURCE = expand([SRC_DIR, "main.c"], delim="/")
    BIN_OUT = expand([SRC_DIR, "main.o"], delim="/")
    BIN_BIN = expand([SRC_DIR, "main.exe"], delim="/")

    bin_build = ccompile(
        CONTEXT,
        CCompileArgs(
            in_=[BIN_SOURCE],
            out=BIN_OUT,
            cc=CC,
            cflags=cflags,
            linking=False,
        ),
    )

    bin = ccompile(
        CONTEXT,
        CCompileArgs(
            in_=[BIN_OUT, *lib_archive.files],
            out=BIN_BIN,
            cc=CC,
            cflags=cflags,
            linking=True,
        ),
    )

    CONTEXT.add_default(bin)

    clean = clean(
        CONTEXT,
        CleanArgs(
            files=[LIB_OUT, BIN_OUT, BIN_BIN, LIB_AR],
            rm=get_rm(CONTEXT),
            rmflags=RMFLAGS,
        ),
    )

with MAKEFILE.open("w") as f:
    CONTEXT.render(f)
