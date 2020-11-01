# pylint: disable=import-error
from sctsock import SCTSock

# pylint: enable=import-error

import os
import json
import tempfile
from fn import run_execute, run_radon
from util.sct_sandbox import filter_source

class GlobalSettings:
    class Exec:
        def __init__(self, data:dict={}):
            self.reset(data)

        def reset(self, data:dict):
            if not isinstance(data, (dict,)):
                data = {}
            self.run: bool = data.get("run", False) == True
            self.mark: bool = data.get("mark", False) == True
            self.pytest: bool = data.get("pytest", False) == True

    class Sandbox:
        def __init__(self, data:dict={}):
            self.imports = []
            self.reset(data)

        def add(self, file, module, allowed):
            if module == None:
                return
            if allowed == None:
                allowed = []
            self.imports.append((file, module, allowed))

        def reset(self, data):
            if not isinstance(data, (dict,)):
                data = {}
            self.imports.clear()
            for entry in data.get("user", ()):
                self.add("*", entry.get("module"), entry.get("allowed"))
            for entry in data.get("test", ()):
                self.add("compare", entry.get("module"), entry.get("allowed"))


    path = os.path.abspath("sct_settings.json")

    def __init__(self, data=None):
        self.reset(data)

    def get_path(self):
        return self.path

    def reset(self, data=None):
        if not isinstance(data, (dict,)):
            data = {}
        self.debug: bool = data.get("debug", False) == True
        self.exec = self.Exec(data.get("exec", {}))
        self.sandbox = self.Sandbox(data.get("sandbox", {}))

        os.makedirs(os.path.dirname(self.get_path()), exist_ok=True)
        with open(self.get_path(), "w") as file:
            file.write(json.dumps(self.sandbox.imports))


class Plugin:
    def __init__(self):
        self.settings = GlobalSettings()
        self.version = None

    def checkVersion(self, version):
        return self.version == version

    def setSettings(self, version, settings):
        print("SetSettings:", version)
        self.version = version
        self.settings.reset(settings)

    def _add_links(self, _dir):
        for (path, _, files) in os.walk("."):
            if os.path.split(path)[1].startswith("tmp_"):
                continue
            for file in files:
                if not file.startswith("sct_"):
                    continue
                try:
                    os.symlink(
                        os.path.abspath(os.path.join(path, file)),
                        os.path.join(_dir, file),
                    )
                except:
                    pass

    def _write_files(self, _dir:str, data:dict):
        code = filter_source(data["code"], "def test_dummy():\n assert True")
        test = filter_source(data["test"], "from sct_test import test, check_args, set_function")
        with open(os.path.join(_dir, "sct_user.py"), "w") as file:
            file.write(code)
        with open(os.path.join(_dir, "sct_compare.py"), "w") as file:
            file.write(test)

    def exec(self, data:dict) -> dict:
        with tempfile.TemporaryDirectory(prefix="tmp_", dir=os.getcwd()) as _dir:
            self._add_links(_dir)
            self._write_files(_dir, data)

            _radon = run_radon(_dir, self.settings)
            _exec = run_execute(_dir, self.settings)
            #return _exec
        return {"radon": _radon, "exec": _exec, "version": self.version}
