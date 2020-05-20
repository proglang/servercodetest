# pylint: disable=import-error
from app.plugins.plugin import Executor as BaseExecutor
from app.util import format
import typing
# pylint: enable=import-error

class Executor(BaseExecutor):
    def get_points(self) -> float:
        return self.points

    def get_error(self) -> typing.Union[str, None]:
        return self.error # machine readable unique key or None

    def get_error_text(self) -> str:
        return format.bold(format.red("an error occured"))# human readable Error Message

    def get_text(self) -> str:
        return self.text

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add stuff you need

    def execute(self):
        self.points = 10
        self.text = "Hello"
        self.error = None
