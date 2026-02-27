from makepy import Context, VariableRef
import sys


def get_python(context: Context) -> VariableRef:
    return context.variable("PYTHON", sys.executable)


def get_printf(context: Context) -> VariableRef:
    return context.variable("PRINTF", "printf")


def get_echo(context: Context) -> VariableRef:
    return context.variable("ECHO", "echo")


def get_rm(context: Context) -> VariableRef:
    return context.variable("RM", "rm")
