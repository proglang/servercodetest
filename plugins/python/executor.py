# pylint: disable=import-error
from app.plugins.plugin.sct_docker import Executor as BaseExecutor
from app.util import format

# pylint: enable=import-error

class Executor(BaseExecutor):
    #! Helper Methods
    def _get_data(self):
        data = self.sct_get_data() or {}
        return (data.get("res", -1), data.get("data", {}))

    def _is_debug(self):
        return self.get_settings().get("debug", False)

    def _get_print_settings(self):
        return self.get_settings().get("print", {})
    def _get_exec_settings(self):
        return self.get_settings().get("exec", {})

    def _is_print_mark(self):
        return self._get_print_settings().get("mark", True)

    def _is_force_mark_output(self):
        return self._get_print_settings().get("force_mark_user_output", False)


    def get_error(self):
        (code, _) = self._get_data()
        if code == 0:
            return None
        if code == 1:
            return "too_many_connections"
        if code == 2:
            return "timeout"
        if code == 3:
            return "container_exception"
        return f"unknown_container_{code}"

    def get_error_text(self) -> str:
        (code, data) = self._get_data()
        if code == 0:
            return ""
        txt = None
        if code == 1:
            txt = "Too many connections to container. please try again later"
        elif code in (2, 3):
            txt = f"A timeout occurred while executing your code ({code})."
        else:
            txt = f"fatal exception in container ({code})."
            if not self._is_debug():
                txt += " activate debug mode for details"
        txt = format.bold(format.red(txt))
        if not self._is_debug():
            return txt
        if code == -1:
            txt += str(data)
        if code == 4:
            txt += "\n\n"
            txt += format.header("TRACEBACK")
            txt += format.red(format.bold(data.get("class", "")))
            txt += ": "
            txt += format.red(data.get("msg", ""))
            txt += "\n"
            for x in data.get("tb", tuple()):
                txt += f" - {format.bold(x['index'])} {format.blue( x['file'])} -> {format.blue(x['func'])}({format.blue(x['line'])}): {format.red(x['code'])}\n"
        return txt

    def _get_run_text(self):
        data = self._get_data()[1]
        data = data.get("exec", {})
        ret = ""
        if (run := data.get("run")) :
            ret += format.section("RUN")
            if (text := run["text"]) != "":
                ret += f"{text}\n"
            if (err := run["error"]) != "":
                ret += f"{format.red(err)}\n"
        return ret
    def _get_pytest_text(self, debug):
        data = self._get_data()[1]
        data = data.get("exec", {})
        ret = ""
        if (pytest := data.get("pytest")) :
            ret += format.section("PYTEST")
            if (text := pytest["text"]) != "":
                ret += f"{text}\n"
            if (err := pytest["error"]) != "":
                ret += f"{format.red(err)}\n"
        return ret
    def _get_mark_text(self, debug):
        data = self._get_data()[1]
        data = data.get("exec", {})

        mark = data.get("mark", None)
        if not mark:
            return ""
        ret = ""
        is_print = self._is_print_mark()
        if not is_print:
            return ""
        is_force_output = self._is_force_mark_output()
        ret = format.section("MARK")
        _add = False
        if debug or is_force_output:
            if (text := mark["text"]) != "":
                ret += f"{text}\n"
                _add = True

        if debug:
            if (err := mark["error"]) != "":
                ret += f"{format.red(err)}\n"
                _add = True
        for key in ("success", "missed"):
            if key in ("missed",) and not debug:
                continue
            if debug:
                ret += format.subsection(key.upper())
            for entry in mark[key]:
                _add = True
                note = entry["note"]
                func = entry["function"]
                points = entry["points"]
                if note != "":
                    ret += f"{func}: {points} => {note}\n"
                else:
                    ret += f"{func}: {points}\n"
        if _add:
             return ret
        return ""

    def get_text(self) -> str:
        code = self._get_data()[0]
        if code != 0:
            return None
        is_dbg = self._is_debug()
        ret = format.header("DEBUGMODE") if is_dbg else ""
        ret += self._get_run_text()
        ret += self._get_pytest_text(is_dbg)
        ret += self._get_mark_text(is_dbg)
        return format.escape_ansi(ret)

    def get_points(self) -> float:
        (code, data) = self._get_data()
        if code != 0:
            return 0
        ret = 0
        data = data.get("exec", {})
        if (mark := data.get("mark")) :
            for entry in mark["success"]:
                ret += entry["points"]
        return ret

