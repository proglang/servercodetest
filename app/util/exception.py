import traceback
import json

from django.conf import settings

from . import log as logging, format

DEBUG = settings.DEBUG

#TODO: Loca

class Traceback:
    class Entry:
        def __init__(self, index, file, line, func, code):
            self.index = index
            self.file = file
            self.line = line
            self.func = func
            self.code = code

        def serialize(self) -> dict:
            return self.__dict__

    def __init__(self, exception: Exception):
        tb = None
        if exception.__traceback__:
            tb = traceback.extract_tb(exception.__traceback__)
            _len = len(tb)
        else:
            tb = traceback.extract_stack()
            _len = len(tb) - 2
        self._class = exception.__class__.__name__
        self.args = exception.args
        data = map(lambda e: (e[0], *e[1]), enumerate(tb))
        data = filter(lambda data: _len > data[0], data)
        self.tb = tuple(map(lambda entry: self.Entry(*entry), data))

    def __str__(self):
        res = [f"== {format.bold(self._class)} =="]
        if DEBUG:
            res.append(f"{self.args!s}")
            formatter = 'f" - {format.bold(entry.index)} {format.blue(entry.file)} -> {format.blue(entry.func)}({format.blue(entry.line)}): {format.red(entry.code)}"'
            res.append("\n".join(map(lambda entry: eval(formatter), self.tb)))
        else:
            res.append("Please activate debug mode for more informations")
        return "\n".join(res)

    def log(self):
        tb = tuple(map(lambda entry: entry.serialize(), self.tb))
        try:
            data = json.dumps({"class": self._class, "args": self.args, "tb": tb})
        except:
            data = json.dumps({"class": self._class, "tb": tb})
        logging.exception(data)


class BaseException(Exception):
    pass
