from dataclasses import dataclass
from typing import (
    Protocol,
    List,
    TypeVar,
    Union,
    Generic,
    Sequence,
    TextIO,
)

# MAKEPY FRAMEWORK


class Consts:
    PHONY = ".PHONY"
    DEFAULT = "default"
    NL = "\n"
    WS = " "
    TAB = "\t"


@dataclass
class VariableRef:
    name: str

    def __str__(self) -> str:
        return f"$({self.name})"


RefOrStr = Union[str, VariableRef]
CommandArgs = Sequence[RefOrStr]


def expand(arg: CommandArgs, delim: str = "") -> str:
    parts = (str(seg) for seg in arg)
    return delim.join(part for part in parts if part)


@dataclass
class MakeBaseRule:
    name: str
    dependencies: CommandArgs
    commands: Sequence[str]

    def emit_into(self, lines: List[str]) -> None:
        expanded = expand(self.dependencies, delim=Consts.WS)

        lines.append(f"{self.name}: {expanded}")
        lines.extend(f"{Consts.TAB}{cmd}" for cmd in self.commands)

    def emit(self) -> str:
        raise NotImplementedError("emit must be implemented by subclasses")


@dataclass
class MakeRule(MakeBaseRule):
    def emit(self) -> str:
        lines: List[str] = []
        self.emit_into(lines)
        return Consts.NL.join(lines)


@dataclass
class MakePhonyRule(MakeBaseRule):
    def emit(self) -> str:
        lines: List[str] = [f"{Consts.PHONY}: {self.name}"]
        self.emit_into(lines)
        return Consts.NL.join(lines)


@dataclass
class MakeVariable:
    name: str
    value: str

    def emit(self) -> str:
        return f"{self.name} = {self.value}"


def command(segments: CommandArgs) -> str:
    return expand(segments, delim=Consts.WS)


def _nl(inp: str, num: int = 1) -> str:
    nls = Consts.NL * num
    return f"{inp}{nls}"


class Info(Protocol):
    files: Sequence[str]


RuleInfo = TypeVar("RuleInfo", bound=Info)


@dataclass
class DefaultInfo(Info):
    files: Sequence[str] = ()


class Context:
    vars: List[MakeVariable]
    rules: List[MakeBaseRule]
    defaults: List[Info]

    def __init__(self):
        self.vars = []
        self.rules = []
        self.defaults = []

    def add_default(self, info: Info) -> None:
        self.defaults.append(info)

    def add_rule(self, rule: MakeBaseRule) -> None:
        self.rules.append(rule)

    def _add_variable(self, var: MakeVariable) -> None:
        self.vars.append(var)

    def variable(self, name: str, value: str) -> VariableRef:
        self._add_variable(MakeVariable(name=name, value=value))
        return VariableRef(name=name)

    def render(self, writer: TextIO) -> None:
        for var in self.vars:
            writer.write(_nl(var.emit(), 1))
        writer.write(_nl("", 1))

        default = MakePhonyRule(
            name=Consts.DEFAULT,
            dependencies=[file for info in self.defaults for file in info.files],
            commands=[],
        )
        writer.write(_nl(default.emit(), 2))

        for rule in self.rules:
            writer.write(_nl(rule.emit(), 1))

        writer.write(_nl("", 1))


RuleArgs = TypeVar("RuleArgs")


class RuleImpl(Protocol[RuleArgs, RuleInfo]):
    def __call__(self, context: Context, args: RuleArgs) -> RuleInfo: ...


class RuleDescribeImpl(Protocol[RuleArgs]):
    def __call__(self, args: RuleArgs) -> str: ...


@dataclass
class Rule(Generic[RuleArgs, RuleInfo]):
    impl: RuleImpl[RuleArgs, RuleInfo]
    describe_impl: RuleDescribeImpl[RuleArgs]

    def __call__(self, context: Context, args: RuleArgs) -> RuleInfo:
        description = self.describe_impl(args)
        print(description)
        return self.impl(context, args)
