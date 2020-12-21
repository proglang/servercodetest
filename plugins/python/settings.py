# pylint: disable=import-error
from app.plugins.plugin import Settings as BaseSettings

# pylint: enable=import-error
from django import forms
from python.container.util.iterator import lines as lineiterator, iterate as iterator

def format_help_text(id, text):
    return f"""<style>#id_{id} + p.help{{display: none;}}</style><pre style="display:inline-block;">{text}</pre>"""
class Form(BaseSettings.Form):
    debug = forms.BooleanField(label="Debug", required=False)
    exec_run = forms.BooleanField(label="Execute Code", required=False)
    exec_mark = forms.BooleanField(label="Mark", required=False)
    print_mark = forms.BooleanField(label="Print Mark Result", required=False)
    exec_pytest = forms.BooleanField(label="Run Pytest", required=False)
    user_import = forms.CharField(
        widget=forms.Textarea(),
        label="Allowed usercode imports", 
        max_length=2048, 
        required=False,
        help_text=format_help_text("user_import","""allowed imports for usercode.
Format:
    module ...
Examples:
    os = allows import os
    os system = allows from os import system
    struct Struct unpack pack = allows from struct import pack, unpack, ...
Do not use multiple lines with the same module import.
Ambiguities won't be resolved.
""")
    )
    test_import = forms.CharField(
        widget=forms.Textarea(), label="Allowed mark code imports", max_length=2048, required=False,
        help_text=format_help_text("test_import","allowed imports for mark code.\nFormat as in usercode.")
    )


class _Exec(BaseSettings):
    def __init__(self, data: dict = {}):
        if not isinstance(data, dict):
            data = {}
        self.run = data.get("run", False)
        self.mark = data.get("mark", False)
        self.pytest = data.get("pytest", False)

class _Print(BaseSettings):
    def __init__(self, data: dict = {}):
        if not isinstance(data, dict):
            data = {}
        self.mark = data.get("mark", True)

class _Sandbox(BaseSettings):
    class Entries:
        class Entry(BaseSettings):
            def __init__(self, data: dict = {}):
                if not isinstance(data, dict):
                    data = {}
                self.module = data.get("module", None)
                self.ignored = data.get("ignored", None)
                self.allowed = data.get("allowed", None)

            def to_string(self):
                if not self.module:
                    return ""
                ret = ""
                if self.ignored:
                    ret += "#"
                ret += self.module + " "
                for entry in self.allowed:
                    ret += entry + " "
                return ret + "\n"

            @classmethod
            def from_string(cls, data: str = ""):
                ret = cls()
                data = data.strip()
                _data = iterator(data, r"[a-zA-Z0-9_.*]+")
                try:
                    ret.module = next(_data)
                    ret.ignored = data[0] == "#"
                    ret.allowed = tuple(_data)
                except:
                    return False
                return ret

        def __init__(self, data: list = []):
            if not isinstance(data, (list, tuple)):
                data = tuple()
            self.entries = list(self.Entry(x) for x in data)

        @classmethod
        def from_string(cls, data: str):
            ret = cls()
            for line in lineiterator(data):
                if (res := cls.Entry.from_string(line)) :
                    ret.entries.append(res)
            return ret

        def to_string(self) -> str:
            ret = ""
            for entry in self.entries:
                ret += entry.to_string()
            return ret

        def serialize(self) -> tuple:
            return tuple(entry.serialize() for entry in self.entries)

    def __init__(self, data: dict = {}):
        if not isinstance(data, dict):
            data = {}
        self.user = self.Entries(data.get("user", []))
        self.test = self.Entries(data.get("test", []))


class Settings(BaseSettings):
    Form = Form

    def __init__(self, data: dict = {}):
        if not isinstance(data, dict):
            data = {}
        self.debug = data.get("debug", False)
        self.sandbox = _Sandbox(data.get("sandbox", {}))
        self.exec = _Exec(data.get("exec", {}))
        self.print = _Print(data.get("print", {}))

    def get_form_data(self):
        ret = {
            "debug": self.debug,
            "exec_run": self.exec.run,
            "exec_mark": self.exec.mark,
            "exec_pytest": self.exec.pytest,
            "user_import": self.sandbox.user.to_string(),
            "test_import": self.sandbox.test.to_string(),
            "print_mark": self.print.mark,
        }
        return ret

    def from_form_data(self, data: dict = {}):
        self.debug = data["debug"]
        self.exec.run = data["exec_run"]
        self.exec.mark = data["exec_mark"]
        self.exec.pytest = data["exec_pytest"]
        self.print.mark = data["print_mark"]
        self.sandbox.user = self.sandbox.user.from_string(data["user_import"])
        self.sandbox.test = self.sandbox.test.from_string(data["test_import"])

