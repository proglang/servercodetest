import typing

from app.util import log as logging

from .executor import Executor
from .settings import Settings
from .request import Request
from .response import Response
from ..info import Info


class Plugin:
    """Base Plugin Class.
    This class defines, which Executor, Settings, Request and Response class is used.
    The Methods defined here should not be overwritten.
    """
    Settings = Settings
    Executor = Executor
    Request = Request
    Response = Response

    def __init__(self, info: Info, path: str):
        with logging.LogCall(__file__, "__init__", self.__class__):
            self.info = info
            self.path = path
            self.logger = logging.PluginLogger(self.info.uid)
            self.logger.debug("%s initialized!", self.__class__.__name__)

    def execute(self, request: Request) -> Response:
        with logging.LogCall(__file__, "execute", self.__class__):
            res = self.Response()
            try:
                exec = self.Executor(self, request)
                exec.execute()
                res.error = exec.get_error()  # pylint: disable=assignment-from-none
                if res.error:
                    res.error_text = exec.get_error_text()
                res.text = exec.get_text()
                res.points = exec.get_points()
            except Exception as e:
                res.set_exception(e)
            return res
