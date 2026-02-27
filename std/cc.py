from makepy import (
    DefaultInfo,
    RefOrStr,
    Context,
    Info,
    MakeRule,
    Rule,
    command,
)
from dataclasses import dataclass
from typing import Sequence


class Consts:
    OUTPUT = "-o"
    CMODE = "-c"


## Compile a single C file


@dataclass
class CCompileArgs:
    in_: Sequence[str]
    out: str
    cc: RefOrStr
    cflags: str
    linking: bool


def ccompile_impl(context: Context, args: CCompileArgs) -> Info:
    modifier = Consts.CMODE if not args.linking else ""

    cmd = command(
        [
            args.cc,
            args.cflags,
            modifier,
            *args.in_,
            Consts.OUTPUT,
            args.out,
        ]
    )

    rule = MakeRule(
        name=args.out,
        dependencies=args.in_,
        commands=[cmd],
    )
    context.add_rule(rule)
    return DefaultInfo(files=[args.out])


def ccompile_impl_describe(args: CCompileArgs) -> str:
    return f"Compiling {args.in_} to {args.out} with {args.cc} and flags {args.cflags}"


ccompile = Rule(impl=ccompile_impl, describe_impl=ccompile_impl_describe)

## Compile multiple C files into multiple object files


@dataclass
class CCompileManyArgs:
    in_: Sequence[str]
    out: Sequence[str]
    cc: RefOrStr
    cflags: RefOrStr


def ccompile_many_impl(context: Context, args: CCompileManyArgs) -> Info:
    def build_command(in_file: str, out_file: str) -> str:
        return command(
            [
                args.cc,
                args.cflags,
                Consts.CMODE,
                in_file,
                Consts.OUTPUT,
                out_file,
            ]
        )

    if len(args.in_) != len(args.out):
        raise ValueError("Input and output file lists must have the same length.")

    for in_file, out_file in zip(args.in_, args.out):
        cmd = build_command(in_file, out_file)
        rule = MakeRule(
            name=out_file,
            dependencies=[in_file],
            commands=[cmd],
        )
        context.add_rule(rule)
    return DefaultInfo(files=args.out)


def ccompile_many_impl_describe(args: CCompileManyArgs) -> str:
    return f"Compiling {args.in_} to {args.out} with {args.cc} and flags {args.cflags}"


ccompile_many = Rule(
    impl=ccompile_many_impl,
    describe_impl=ccompile_many_impl_describe,
)
