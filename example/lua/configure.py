from makepy import (
    Context,
    expand,
    VariableRef,
    Info,
    MakePhonyRule,
    command,
    Rule,
    DefaultInfo,
    MakeRule,
)
from std.bins import get_rm, get_echo
from std.cc import ccompile, CCompileArgs, ccompile_many, CCompileManyArgs
from std.packaging import archive, ArchiveArgs, clean, CleanArgs
from pathlib import Path


## Context and paths
CONTEXT = Context()
ROOT_DIR = Path(__file__).parent
MAKEFILE = ROOT_DIR / "makefile"
LUA_DIR_PATH = ROOT_DIR / "lua"

LUA_DIR = CONTEXT.variable("LUA_DIR", str(LUA_DIR_PATH))
ALL_FILE = CONTEXT.variable("ALL_FILE", expand([LUA_DIR, "all"], delim="/"))


# == CHANGE THE SETTINGS BELOW TO SUIT YOUR ENVIRONMENT =======================

# Warnings valid for both C and C++
CWARNSCPP = CONTEXT.variable(
    "CWARNSCPP",
    expand(
        [
            "-Wfatal-errors",
            "-Wextra",
            "-Wshadow",
            "-Wundef",
            "-Wwrite-strings",
            "-Wredundant-decls",
            "-Wdisabled-optimization",
            "-Wdouble-promotion",
            "-Wmissing-declarations",
            "-Wconversion",
        ],
        delim=" ",
    ),
)

# Warnings for gcc, not valid for clang
CWARNGCC = CONTEXT.variable(
    "CWARNGCC",
    expand(
        [
            "-Wlogical-op",
            "-Wno-aggressive-loop-optimizations",
        ],
        delim=" ",
    ),
)

# The next warnings are neither valid nor needed for C++
CWARNSC = CONTEXT.variable(
    "CWARNSC",
    expand(
        [
            "-Wdeclaration-after-statement",
            "-Wmissing-prototypes",
            "-Wnested-externs",
            "-Wstrict-prototypes",
            "-Wc++-compat",
            "-Wold-style-definition",
        ],
        delim=" ",
    ),
)

CWARNS = CONTEXT.variable(
    "CWARNS",
    expand(
        [CWARNSCPP, CWARNGCC, CWARNSC],
        delim=" ",
    ),
)

# Some useful compiler options for internal tests:
# -DLUAI_ASSERT turns on all assertions inside Lua.
# -DHARDSTACKTESTS forces a reallocation of the stack at every point where
# the stack can be reallocated.
# -DHARDMEMTESTS forces a full collection at all points where the collector
# can run.
# -DEMERGENCYGCTESTS forces an emergency collection at every single allocation.
# -DEXTERNMEMCHECK removes internal consistency checking of blocks being
# deallocated (useful when an external tool like valgrind does the check).
# -DMAXINDEXRK=k limits range of constants in RK instruction operands.
# -DLUA_COMPAT_5_3

# -pg -malign-double
# -DLUA_USE_CTYPE -DLUA_USE_APICHECK

# The following options help detect "undefined behavior"s that seldom
# create problems; some are only available in newer gcc versions. To
# use some of them, we also have to define an environment variable
# ASAN_OPTIONS="detect_invalid_pointer_pairs=2".
# -fsanitize=undefined
# -fsanitize=pointer-subtract -fsanitize=address -fsanitize=pointer-compare
# TESTS= -DLUA_USER_H='"ltests.h"' -Og -g


LOCAL = CONTEXT.variable(
    "LOCAL", expand([VariableRef(name="TESTS"), CWARNS], delim=" ")
)

# To enable Linux goodies, -DLUA_USE_LINUX
# For C89, "-std=c89 -DLUA_USE_C89"
# Note that Linux/Posix options are not compatible with C89
MYCFLAGS = CONTEXT.variable(
    "MYCFLAGS", expand([LOCAL, "-std=c99", "-DLUA_USE_LINUX"], delim=" ")
)
MYLDFLAGS = CONTEXT.variable("MYLDFLAGS", "-Wl,-E")
MYLIBS = CONTEXT.variable("MYLIBS", "-ldl")

## Binaries
CC = CONTEXT.variable("CC", "gcc")
CFLAGS = CONTEXT.variable(
    "CFLAGS",
    expand(
        [
            "-Wall",
            "-O2",
            MYCFLAGS,
            "-fno-stack-protector",
            "-fno-common",
            "-march=native",
        ],
        delim=" ",
    ),
)

AR = CONTEXT.variable("AR", "ar")
ARFLAGS = CONTEXT.variable("ARFLAGS", "rcs")

RANLIB = CONTEXT.variable("RANLIB", "ranlib")

RM = get_rm(CONTEXT)
RMFLAGS = CONTEXT.variable("RMFLAGS", "-rf")

TOUCH = CONTEXT.variable("TOUCH", "touch")
ECHO = get_echo(CONTEXT)

# == END OF USER SETTINGS. NO NEED TO CHANGE ANYTHING BELOW THIS LINE =========

LIBS = CONTEXT.variable("LIBS", "-lm")

## Targets

"""
CORE_T=	liblua.a
CORE_O=	lapi.o lcode.o lctype.o ldebug.o ldo.o ldump.o lfunc.o lgc.o llex.o \
	lmem.o lobject.o lopcodes.o lparser.o lstate.o lstring.o ltable.o \
	ltm.o lundump.o lvm.o lzio.o ltests.o
AUX_O=	lauxlib.o
LIB_O=	lbaselib.o ldblib.o liolib.o lmathlib.o loslib.o ltablib.o lstrlib.o \
	lutf8lib.o loadlib.o lcorolib.o linit.o

LUA_T=	lua
LUA_O=	lua.o

"""

ALL_C_FILES = [p.name for p in LUA_DIR_PATH.glob("*.c")]
EXPANDED_ALL_C_FILES = [expand([LUA_DIR, c], delim="/") for c in ALL_C_FILES]
ALL_H_FILES = [p.name for p in LUA_DIR_PATH.glob("*.h")]
EXPANDED_ALL_H_FILES = [expand([LUA_DIR, h], delim="/") for h in ALL_H_FILES]

ALL_O_FILES = [f.replace(".c", ".o") for f in ALL_C_FILES]
EXPANDED_ALL_O_FILES = [expand([LUA_DIR, o], delim="/") for o in ALL_O_FILES]

CORE_TARGET = CONTEXT.variable("CORE_T", expand([LUA_DIR, "liblua.a"], delim="/"))
CORE_OBJS = CONTEXT.variable(
    "CORE_OBJS",
    expand(
        [
            expand([LUA_DIR, "lapi.o"], delim="/"),
            expand([LUA_DIR, "lcode.o"], delim="/"),
            expand([LUA_DIR, "lctype.o"], delim="/"),
            expand([LUA_DIR, "ldebug.o"], delim="/"),
            expand([LUA_DIR, "ldo.o"], delim="/"),
            expand([LUA_DIR, "ldump.o"], delim="/"),
            expand([LUA_DIR, "lfunc.o"], delim="/"),
            expand([LUA_DIR, "lgc.o"], delim="/"),
            expand([LUA_DIR, "llex.o"], delim="/"),
            expand([LUA_DIR, "lmem.o"], delim="/"),
            expand([LUA_DIR, "lobject.o"], delim="/"),
            expand([LUA_DIR, "lopcodes.o"], delim="/"),
            expand([LUA_DIR, "lparser.o"], delim="/"),
            expand([LUA_DIR, "lstate.o"], delim="/"),
            expand([LUA_DIR, "lstring.o"], delim="/"),
            expand([LUA_DIR, "ltable.o"], delim="/"),
            expand([LUA_DIR, "ltm.o"], delim="/"),
            expand([LUA_DIR, "lundump.o"], delim="/"),
            expand([LUA_DIR, "lvm.o"], delim="/"),
            expand([LUA_DIR, "lzio.o"], delim="/"),
            expand([LUA_DIR, "ltests.o"], delim="/"),
        ],
        delim=" ",
    ),
)

AUX_OBJS = CONTEXT.variable(
    "AUX_OBJS",
    expand(
        [
            expand([LUA_DIR, "lauxlib.o"], delim="/"),
        ],
        delim=" ",
    ),
)

LUA_TARGET = CONTEXT.variable("LUA_T", expand([LUA_DIR, "lua"], delim="/"))
LIB_OBJS = CONTEXT.variable(
    "LIB_OBJS",
    expand(
        [
            expand([LUA_DIR, "lbaselib.o"], delim="/"),
            expand([LUA_DIR, "ldblib.o"], delim="/"),
            expand([LUA_DIR, "liolib.o"], delim="/"),
            expand([LUA_DIR, "lmathlib.o"], delim="/"),
            expand([LUA_DIR, "loslib.o"], delim="/"),
            expand([LUA_DIR, "ltablib.o"], delim="/"),
            expand([LUA_DIR, "lstrlib.o"], delim="/"),
            expand([LUA_DIR, "lutf8lib.o"], delim="/"),
            expand([LUA_DIR, "loadlib.o"], delim="/"),
            expand([LUA_DIR, "lcorolib.o"], delim="/"),
            expand([LUA_DIR, "linit.o"], delim="/"),
        ],
        delim=" ",
    ),
)

LUA_OBJS = CONTEXT.variable(
    "LUA_OBJS",
    expand(
        [
            CORE_OBJS,
            AUX_OBJS,
            LIB_OBJS,
            expand([LUA_DIR, "lua.o"], delim="/"),
        ],
        delim=" ",
    ),
)

"""
ALL_T= $(CORE_T) $(LUA_T)
ALL_O= $(CORE_O) $(LUA_O) $(AUX_O) $(LIB_O)
ALL_A= $(CORE_T)
"""

ALL_TARGET = CONTEXT.variable("ALL_T", expand([CORE_TARGET, LUA_TARGET], delim=" "))
ALL_OBJS = CONTEXT.variable(
    "ALL_O",
    expand(
        [CORE_OBJS, LUA_OBJS],
        delim=" ",
    ),
)
ALL_ARCHIVE = CONTEXT.variable("ALL_A", CORE_TARGET)

"""

all:	$(ALL_T)
	touch all

o:	$(ALL_O)

a:	$(ALL_A)

"""


def all_impl(context: Context, _: None) -> Info:
    touch_all = command([TOUCH, ALL_FILE])

    rule = MakePhonyRule(
        name="all",
        dependencies=[CORE_TARGET, LUA_TARGET],
        commands=[touch_all],
    )

    context.add_rule(rule)
    return DefaultInfo(files=[CORE_TARGET, LUA_TARGET])


all = Rule(impl=all_impl, describe_impl=lambda _: "Generating all targets")(
    CONTEXT, None
)
CONTEXT.add_default(all)


def o_impl(context: Context, _: None) -> Info:
    rule = MakePhonyRule(
        name="o",
        dependencies=[ALL_OBJS],
        commands=[],
    )

    context.add_rule(rule)
    return DefaultInfo(files=ALL_OBJS)


Rule(impl=o_impl, describe_impl=lambda _: "Generating all object files")(CONTEXT, None)


def a_impl(context: Context, _: None) -> Info:
    rule = MakePhonyRule(
        name="a",
        dependencies=[ALL_ARCHIVE],
        commands=[],
    )

    context.add_rule(rule)
    return DefaultInfo(files=ALL_ARCHIVE)


Rule(impl=a_impl, describe_impl=lambda _: "Generating the archive")(CONTEXT, None)

"""
$(CORE_T): $(CORE_O) $(AUX_O) $(LIB_O)
	$(AR) $@ $?
	$(RANLIB) $@

$(LUA_T): $(LUA_O) $(CORE_T)
	$(CC) -o $@ $(MYLDFLAGS) $(LUA_O) $(CORE_T) $(LIBS) $(MYLIBS) $(DL)

"""

archive(
    CONTEXT,
    ArchiveArgs(
        in_=[CORE_OBJS, AUX_OBJS, LIB_OBJS],
        out=CORE_TARGET,
        ar=AR,
        arflags=ARFLAGS,
    ),
)

CFLAGS_LUA = expand(
    [MYLDFLAGS, LIBS, MYLIBS, VariableRef(name="DL")],
    delim=" ",
)

ccompile(
    CONTEXT,
    CCompileArgs(
        in_=[LUA_OBJS, CORE_TARGET],
        out=LUA_TARGET,
        cc=CC,
        cflags=CFLAGS_LUA,
        linking=True,
    ),
)

"""
clean:
	$(RM) $(ALL_T) $(ALL_O)

depend:
	@$(CC) $(CFLAGS) -MM *.c

echo:
	@echo "CC = $(CC)"
	@echo "CFLAGS = $(CFLAGS)"
	@echo "AR = $(AR)"
	@echo "RANLIB = $(RANLIB)"
	@echo "RM = $(RM)"
	@echo "MYCFLAGS = $(MYCFLAGS)"
	@echo "MYLDFLAGS = $(MYLDFLAGS)"
	@echo "MYLIBS = $(MYLIBS)"
	@echo "DL = $(DL)"
"""

clean(
    CONTEXT,
    CleanArgs(
        files=[ALL_TARGET, ALL_OBJS],
        rm=RM,
        rmflags=RMFLAGS,
    ),
)


def depend_impl(context: Context, _: None) -> Info:
    cmd = command([CC, CFLAGS, "-MM", expand([LUA_DIR, "*.c"], delim="/")])
    rule = MakePhonyRule(name="depend", dependencies=[], commands=[cmd])
    context.add_rule(rule)
    return DefaultInfo(files=[])


Rule(impl=depend_impl, describe_impl=lambda _: "Generating dependencies")(CONTEXT, None)


def echo_impl(context: Context, _: None) -> Info:
    cmds = [
        command([ECHO, f"CC = {CC}"]),
        command([ECHO, f"CFLAGS = {CFLAGS}"]),
        command([ECHO, f"AR = {AR}"]),
        command([ECHO, f"RANLIB = {RANLIB}"]),
        command([ECHO, f"RM = {RM}"]),
        command([ECHO, f"MYCFLAGS = {MYCFLAGS}"]),
        command([ECHO, f"MYLDFLAGS = {MYLDFLAGS}"]),
        command([ECHO, f"MYLIBS = {MYLIBS}"]),
        command([ECHO, f"DL = {VariableRef(name='DL')}"]),
    ]

    rule = MakePhonyRule(name="echo", dependencies=[], commands=cmds)
    context.add_rule(rule)
    return DefaultInfo(files=[])


Rule(impl=echo_impl, describe_impl=lambda _: "Echoing configuration")(CONTEXT, None)

"""
$(ALL_O): makefile ltests.h
"""


def all_o_impl(context: Context, _: None) -> Info:
    rule = MakeRule(
        name=ALL_OBJS,
        dependencies=[
            MAKEFILE,
            expand([LUA_DIR, "ltests.h"], delim="/"),
            *EXPANDED_ALL_H_FILES,
        ],
        commands=[],
    )

    context.add_rule(rule)
    return DefaultInfo(files=ALL_OBJS)


Rule(
    impl=all_o_impl, describe_impl=lambda _: "Adding dependencies for all object files"
)(CONTEXT, None)

"""
Compile lua:
"""

ccompile_many(
    CONTEXT,
    CCompileManyArgs(
        in_=[*EXPANDED_ALL_C_FILES],
        out=EXPANDED_ALL_O_FILES,
        cc=CC,
        cflags=CFLAGS,
    ),
)

## Render
with MAKEFILE.open("w") as f:
    CONTEXT.render(f)
