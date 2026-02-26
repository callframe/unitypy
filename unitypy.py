from dataclasses import dataclass
from typing import Optional, Protocol, List, TypeVar, Any, Union, Generic

# RESULT IMPLEMENTATION

ResultT = TypeVar("ResultT")
ResultE = TypeVar("ResultE")


@dataclass
class ResultOk(Generic[ResultT]):
    value: ResultT


@dataclass
class ResultErr(Generic[ResultE]):
    error: ResultE


Result = Union[ResultOk[ResultT], ResultErr[ResultE]]

# UNITYPY FRAMEWORK


@dataclass
class Context:
    pass


class RuleError(Protocol):
    def what(self) -> str: ...


class Info(Protocol):
    files: List[str]


InfoReturn = TypeVar("InfoReturn", bound=Info)
RuleImplReturn = Result[InfoReturn, RuleError]


class RuleImpl(Protocol[InfoReturn]):
    def __call__(self, context: Context, **kwargs: Any) -> RuleImplReturn: ...


@dataclass
class DefaultInfo(Info):
    files: List[str]


RuleArgs = dict[str, type]


@dataclass
class Rule(Generic[InfoReturn]):
    name: str
    impl: RuleImpl
    args: RuleArgs

    def __call__(self, context: Context, **kwargs: Any) -> RuleImplReturn:
        return self._call(context, **kwargs)

    def _call_check_missing(self, kwargs: RuleArgs) -> Optional[RuleError]:
        for key in self.args:
            if key not in kwargs:
                return RuleErrorArgMissing(argument=key, rule=self)
        return None

    def _call_check_unknown(self, kwargs: RuleArgs) -> Optional[RuleError]:
        for key in kwargs:
            if key not in self.args:
                return RuleErrorArgUnknown(
                    argument=key, argument_type=type(kwargs[key]), rule=self
                )
        return None

    def _call_check_mismatch(self, kwargs: RuleArgs) -> Optional[RuleError]:
        for key in kwargs:
            if key in self.args and not isinstance(kwargs[key], self.args[key]):
                return RuleErrorArgTypeMismatch(
                    argument=key,
                    expected_type=self.args[key],
                    actual_type=type(kwargs[key]),
                    rule=self,
                )
        return None

    def _call(self, context: Context, **kwargs: RuleArgs) -> RuleImplReturn:
        error = self._call_check_missing(kwargs)
        if error:
            return ResultErr(error)

        error = self._call_check_unknown(kwargs)
        if error:
            return ResultErr(error)

        error = self._call_check_mismatch(kwargs)
        if error:
            return ResultErr(error)

        return self.impl(context, **kwargs)


@dataclass
class RuleErrorArgUnknown:
    argument: str
    argument_type: type
    rule: Rule

    def what(self) -> str:
        return (
            f"unknown argument '{self.argument}' "
            f"of type {self.argument_type.__name__} "
            f"in rule '{self.rule.name}'"
        )


@dataclass
class RuleErrorArgTypeMismatch:
    argument: str
    expected_type: type
    actual_type: type
    rule: Rule

    def what(self) -> str:
        return (
            f"argument '{self.argument}' has type {self.actual_type.__name__} "
            f"but expected {self.expected_type.__name__} "
            f"in rule '{self.rule.name}'"
        )


@dataclass
class RuleErrorArgMissing:
    argument: str
    rule: Rule

    def what(self) -> str:
        return f"missing argument '{self.argument}' in rule '{self.rule.name}'"


# Example


def compile_c_impl(
    context: Context, inp: str, outp: str, cflags: str
) -> RuleImplReturn:
    print(f"Compiling {inp} to {outp} with flags {cflags}")
    return ResultOk(DefaultInfo(files=[outp]))


compile_c = Rule(
    name="compile_c",
    impl=compile_c_impl,
    args={"inp": str, "outp": str, "cflags": str},
)

if __name__ == "__main__":
    context = Context()
    result = compile_c(
        context,
        inp="main.c",
        outp="main.o",
        cflags="-O2 -Wall",
    )

    if isinstance(result, ResultOk):
        print(f"Compilation succeeded, generated files: {result.value.files}")
    else:
        print(f"Compilation failed with error: {result.error.what()}")
