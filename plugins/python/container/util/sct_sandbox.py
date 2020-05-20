import re
import typing
import builtins
import os
import json


class SandboxError(RuntimeError):
    pass


FORBIDDEN_FUNCTIONS = {
    "eval",
    "exec",
    "open",
    "globals",
    "locals",
    "breakpoint",
    "copyright",
    "credits",
    "license",
    "memoryview",
    "getattr",
}
FORBIDDEN_ATTRIBUTES = {
    "__untrusted__",
    "__dict__",
    "builtins",
    "__builtins__",
    "__file__",
    "__main__",
    #"__name__",
    "__loader__",
}


def filter_source(src: str, header: str = ""):
    for key in FORBIDDEN_FUNCTIONS:
        src = re.sub(
            f"([^.a-zA-Z0-9_])({key})([^a-zA-Z0-9_])", r"\1_sandboxed_.\2\3", src
        )
        src = re.sub(f"(def|class)\\s+_sandboxed_.({key})", r"\1 \2", src)

        # imports
        src = re.sub(f"import\\s+_sandboxed_.({key})\\s+as", r"import \1 as", src)
        src = re.sub(f"import\\s+_sandboxed_.({key})", r"import \1 as _\1_", src)
        src = re.sub(f"([\\s,])_sandboxed_.({key})\\s+as", r"\1\2 as", src)

    for key in FORBIDDEN_ATTRIBUTES:
        src = re.sub(
            f"([^a-zA-Z0-9_])({key})([^a-zA-Z0-9_])", r"\1_sandboxed_.\2\3", src
        )
    res = f"{header}\n"
    res = f"{res}from sct_sandbox import init, SandboxError\n"
    res = f"{res}_sandboxed_ = init()\n"
    res = f"{res}import __untrusted__\n"
    res = f"{res}{src}\n"
    return res


class Sandbox:
    @staticmethod
    def _get_attribute(obj, name):
        if name in FORBIDDEN_FUNCTIONS:
            raise SandboxError(f"Cannot access {name}: forbidden!")
        if name in FORBIDDEN_ATTRIBUTES:
            raise SandboxError(f"Cannot access {name}: forbidden!")
        return getattr(obj, name)

    @classmethod
    def __getattribute__(cls, name):
        #if name == "__name__":
        #    return "__main__"
        if name == "getattr":
            return Sandbox._get_attribute
        raise SandboxError(f"Cannot access {name}: forbidden!")


class ImportFilter:
    class Entry:
        def __init__(self, module: str, name: str, allowed: set = None):
            self.name = name
            self.module = module
            self.allowed: typing.Set[str] = allowed or {}

        def check(self, module, named):
            if len(self.allowed) == 0:
                return True
            if len(named) == 0:
                raise SandboxError(f"Cannot import {self.name}: specify imports...")
            if "*" in named:
                raise SandboxError(f"Cannot import {self.name}: * forbidden")
            for name in named:
                if len(self.allowed) == 0:
                    continue
                if name in self.allowed:
                    continue
                raise SandboxError(f"Cannot import {self.name}: {name} forbidden")
            return True

        def __repr__(self):
            return f"<<{self.name} {self.module} {str(self.allowed)}>>"

    modules: typing.Dict[str, typing.List[Entry]] = {}

    @classmethod
    def check(cls, module, name, namedimports=()):
        if not name in cls.modules:
            raise SandboxError(f"Cannot import {name}: forbidden")
        for entry in cls.modules[name]:
            if entry.module != "*":
                if not entry.module in module:
                    continue
            entry.check(module, namedimports)
            return True
        raise SandboxError(f"Cannot import {name}: forbidden for this module...")

    @classmethod
    def add(
        cls, module: str, name: str, allowed: typing.Set[str] = None,
    ):
        if not name in cls.modules:
            cls.modules[name] = []
        cls.modules[name].append(cls.Entry(module, name, allowed))


__orig__import = None


def __import(name: str, globals=None, locals=None, fromlist=(), *args, **kwargs):
    if name == "__untrusted__":
        return None
    if globals == None:
        pass
    elif globals.get("__untrusted__", True) != True:
        if name.startswith("sct_"):
            raise SandboxError(f"Cannot import {name}: forbidden!")
        module = globals.get("__name__", "")
        ImportFilter.check(module, name, fromlist or ())
    module = __orig__import(name, globals, locals, fromlist, *args, **kwargs)
    return module


def init():
    global __orig__import
    if __orig__import == None:
        __orig__import = builtins.__import__
    builtins.__import__ = __import
    path = os.path.join(os.path.dirname(__file__), "sct_settings.json")
    with open(path) as settings:
        for entry in json.load(settings):
            ImportFilter.add(*entry)
    return Sandbox
