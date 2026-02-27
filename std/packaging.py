from makepy import (
    RefOrStr,
    Context,
    Info,
    MakeRule,
    Rule,
    command,
    DefaultInfo,
    MakePhonyRule,
)
from dataclasses import dataclass
from typing import Sequence


## Archive objects into a static library
@dataclass
class ArchiveArgs:
    in_: Sequence[str]
    out: str
    ar: RefOrStr
    arflags: RefOrStr


@dataclass
class ArchiveInfo(Info):
    files: Sequence[str]
    lib: str


def archive_impl(context: Context, args: ArchiveArgs) -> ArchiveInfo:
    cmd = command([args.ar, args.arflags, args.out, *args.in_])

    rule = MakeRule(
        name=args.out,
        dependencies=args.in_,
        commands=[cmd],
    )
    context.add_rule(rule)

    return ArchiveInfo(files=[args.out], lib=args.out)


def archive_impl_describe(args: ArchiveArgs) -> str:
    return f"Generating archiving rule for {args.in_} to {args.out}"


archive = Rule(impl=archive_impl, describe_impl=archive_impl_describe)


## Clean files
@dataclass
class CleanArgs:
    files: Sequence[str]
    rm: RefOrStr
    rmflags: RefOrStr


def clean_impl(context: Context, args: CleanArgs) -> Info:
    cmd = command([args.rm, args.rmflags, *args.files])
    rule = MakePhonyRule(name="clean", dependencies=[], commands=[cmd])
    context.add_rule(rule)
    return DefaultInfo()


def clean_impl_describe(args: CleanArgs) -> str:
    return f"Generating clean rule for {len(args.files)} files"


clean = Rule(impl=clean_impl, describe_impl=clean_impl_describe)
