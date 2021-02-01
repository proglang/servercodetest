import util
import util.random
import os
import json
from .struct import Output, Text, Mark
import logging
class Main:
    def __init__(
        self, _dir: str, globalSettings: "GlobalSettings",
    ):
        from plugin import GlobalSettings

        self.dir = _dir
        self.delimiter = "DATA_" + util.random.string(20)
        self._global: GlobalSettings = globalSettings

    def _get_env(self):
        env = {
            "PYTHONHASHSEED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "DELIMITER": self.delimiter,
        }
        # TODO: remove non needed env vars
        for k, v in os.environ.items():
            env[k] = v
        return env

    def _parse(self, data:str) -> dict:
        try:
            start_tag1 = data.rfind(f"<{self.delimiter}>")
            end_tag1 = start_tag1 + len(self.delimiter) + 2
            start_tag2 = data.find(f"</{self.delimiter}>", end_tag1)
            return (data[:start_tag1], json.loads(data[end_tag1:start_tag2]))
        except Exception as e:
            logging.error("Couldn't parse result: %s -> data: %s", str(e), str(data))
            return (data, {})

    def _popen(self, *args):
        return util.Popen(*args, env=self._get_env(), cwd=self.dir)

    def run_code(self):
        try:
            logging.debug("run_code->start")
            popen = self._popen("python3", "./sct_user.py")
            return Text(popen.error, popen.data)
        except Exception as e:
            logging.error("Exception in run_code: %s", str(e))
            raise #forward excpetion
        finally:
            logging.debug("run_code->finish")

    def run_pytest(self):
        try:
            logging.debug("run_pytest->start")
            popen = self._popen("pytest", "./sct_user.py", "--color=yes")
            return Text(popen.error, popen.data)
        except Exception as e:
            logging.error("Exception in run_pytest: %s", str(e))
            raise #forward excpetion
        finally:
            logging.debug("run_pytest->finish")

    def run_mark(self):
        try:
            logging.debug("run_mark->start")
            popen = self._popen("python3", "./sct_exec_mark.py")
            (text, data) = self._parse(popen.data)
            ret = Mark(popen.error, text)
            for (_, value) in data.items():
                for entry in value["reg"]:
                    ret.add(*entry, False)
                for entry in value["suc"]:
                    ret.add(*entry, True)
        except Exception as e:
            logging.error("Exception in run_mark: %s", str(e))
            raise #forward excpetion
        finally:
            logging.debug("run_mark->finish")
        return ret

    def run(self):
        output = Output()
        if self._global.exec.run:
            output.run = self.run_code()
        if self._global.exec.pytest:
            output.pytest = self.run_pytest()
        if self._global.exec.mark:
            output.mark = self.run_mark()
        return output.serialize()
