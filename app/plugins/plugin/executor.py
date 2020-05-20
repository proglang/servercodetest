import typing

from app.util import log as logging

from ..info import Info


class Executor:
    """ Basic Executor Class
        All methods should be implemented in derived classes.
    """
    def get_points(self) -> float:
        return 0

    def get_error(self) -> typing.Union[str, None]:
        return None

    def get_error_text(self) -> str:
        return ""

    def get_text(self) -> str:
        return ""

    # DO NOT OVERWRITE METHODS BELOW
    # except you know what you're doing
    #
    # look at docker/executor.py, sct/executor.py or sct_docker/executor.py
    # for examples
    def __init__(self, plugin, request, *args, **kwargs):
        with logging.LogCall(__file__, "__init__", self.__class__):
            self.request = request
            self.plugin = plugin
            self.logger = logging.PluginLogger(plugin.info.uid)
            self.logger.debug("Initializing %s", self.__class__.__name__)

    def execute(self):
        with logging.LogCall(__file__, "execute", self.__class__):
            self.logger.critical(
                "execute is not implemented by %s", self.__class__.__name__
            )
            raise NotImplementedError

