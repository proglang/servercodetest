from app.util.exception import Traceback


class Response:
    def __init__(self):
        self.error = None
        self.error_text = None
        self.text = None
        self.points = None

    def has_error(self):
        return isinstance(self.error, str)

    def set_exception(self, e: Exception):
        self.error = "exception"
        tb = Traceback(e)
        self.error_text = str(tb)
        tb.log()

    def serialize(self):
        res = {}
        if isinstance(self.points, (int, float)):
            res["points"] = max(0, self.points)
        if isinstance(self.text, str):
            res["text"] = self.text
        if isinstance(self.error, str):
            _res = {"key": self.error}
            if isinstance(self.error_text, str):
                _res["text"] = self.error_text
            res["error"] = _res
        return res

