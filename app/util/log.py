import logging
import os

from django.conf import settings


logging.addLevelName(5, "TRACE")
logging.basicConfig(
    format="%(name)s:%(levelname)s:%(process)x:%(thread)x:%(created).4f:%(message)s"
)


def get_level():
    return {k.upper(): v for k, v in logging._nameToLevel.items()}


def get_level_by_level(level) -> int:
    if type(level) == str:
        return get_level().get(level.strip().upper(), 0)
    if type(level) == int:
        return level
    return 0


LOG_LEVEL = get_level_by_level(settings.LOG_LEVEL)
ROOT_DIR = settings.ROOT_DIR


class LogCall:
    def __init__(self, file: str, name: str, _class=None, logger=None):
        self.file = os.path.relpath(file, ROOT_DIR)
        if isinstance(_class, type):
            self.name = f"{_class.__name__}.{name}"
        else:
            self.name = name
        self.logger = logger if logger else main_logger

    def __enter__(self):
        self.logger.trace(">:%s:%s", self.name, self.file)
        return self

    def __exit__(self, error, error_message, traceback):
        self.logger.trace(
            "<:%s:%s:%s", self.name, self.file, type(error).__name__ if error else False
        )
        if error:
            raise


class Logger:
    def __init__(self, name):
        self.logger: logging.Logger = logging.getLogger(name)
        self.logger.setLevel(LOG_LEVEL)

    def get(self) -> logging.Logger:
        return self.logger

    def get_trace(self, file: str, name: str, _class=None) -> LogCall:
        return LogCall(file, name, _class, self)

    def trace(self, *args, **kwargs):
        return self.logger.log(5, *args, **kwargs)

    def debug(self, *args, **kwargs):
        return self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        return self.logger.critical(*args, **kwargs)

    def exception(self, *args, **kwargs):
        return self.logger.exception(*args, **kwargs)


class PluginLogger(Logger):
    def __init__(self, name):
        super().__init__("sct_plugin." + name)


main_logger = Logger("sct_main")
trace = main_logger.trace
debug = main_logger.debug
info = main_logger.info
warning = main_logger.warning
error = main_logger.error
critical = main_logger.critical
exception = main_logger.exception
