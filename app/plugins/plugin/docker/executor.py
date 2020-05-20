from django.conf import settings as django_settings

from ..executor import Executor as BaseExecutor
from ...exception import PluginException

from app.util import log as logging
from app.util.docker import Container, Image


class Executor(BaseExecutor):
    """ This Executor manages docker-containers.
        Containers are automatically created when they are needed.
        you need to call 'execute' at the top of your execute Method.
    """
    def __init__(self, *args, **kwargs):
        with logging.LogCall(__file__, "__init__", self.__class__):
            super().__init__(*args, **kwargs)
            self._docker_container = Container(self.request.token)
            self._docker_image = Image(self.plugin.info.uid, self.plugin.info.version)

    def _start_container(self):
        with logging.LogCall(__file__, "_start_container", self.__class__):
            c = self._docker_container
            if c.exists():
                if c.is_running():
                    self.logger.debug(
                        "Container(%s) is running",
                        self._docker_container.container_name,
                    )
                    return True
            else:
                if self._docker_image.create(self.plugin.path):
                    self.logger.debug(
                        "Image(%s) created", self._docker_image.image_name
                    )
                if self._docker_container.create(self._docker_image):
                    self.logger.debug(
                        "Container(%s) created", self._docker_container.container_name
                    )
            if self._docker_container.start():
                self.logger.debug(
                    "Container(%s) started", self._docker_container.container_name
                )
            return True

    def get_container_name(self):
        return self._docker_container.container_name

    def execute(self):
        with logging.LogCall(__file__, "execute", self.__class__):
            if django_settings.DOCKER_ENABLED != True:
                raise PluginException("Container disabled")
            self._start_container()
