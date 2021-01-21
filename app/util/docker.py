import docker
import typing
import os

from django.conf import settings

from . import log as logging
from .lock import LockHandler

PREFIX = settings.DOCKER_PREFIX
DOCKER_NETWORK = settings.DOCKER_NETWORK
DOCKER_ENABLED = settings.DOCKER_ENABLED


LockHandler.register("docker")


ContainerType = docker.models.containers.Container
ImageType = docker.models.images.Image


class _Docker:
    client = docker.from_env() if DOCKER_ENABLED else None

    @classmethod
    def get(cls):
        if cls.client:
            return cls.client
        raise Exception("docker is disabled")


class _Container:
    @classmethod
    def get(cls, name: str) -> ContainerType:
        return _Docker.get().containers.get(name)

    @classmethod
    def create(cls, image: str, name: str, network: str) -> ContainerType:
        return _Docker.get().containers.create(image, name=name, network=network)

    @classmethod
    def ls(cls, filter=None) -> typing.List[ContainerType]:
        return _Docker.get().containers.list(
            all=True, filters={"name": f"{PREFIX}_{filter or '*'}"}
        )

    @classmethod
    def by_image(cls, filter: str) -> typing.List[ContainerType]:
        res = _Docker.get().containers.list(all=True, filters={"ancestor": filter})
        res = tuple(x for x in res if x.attrs["Config"]["Image"] == filter)
        return res

    @classmethod
    def start(cls, name: str) -> ContainerType:
        cnt = cls.get(name)
        networks = cnt.attrs.get("NetworkSettings", {}).get("Networks", {})
        for network in networks:
            n = _Docker.get().networks.get(network)
            n.disconnect(cnt)
        cnt.start()          
        for network in networks:
            n = _Docker.get().networks.get(network)
            n.connect(cnt)
        return cnt

    @classmethod
    def stop(cls, name: str) -> ContainerType:
        cnt = cls.get(name)
        cnt.stop()
        return cnt

    @classmethod
    def delete(cls, name: str):
        cnt = cls.get(name)
        cnt.remove()


class _Image:
    @classmethod
    def get(cls, name: str) -> ImageType:
        return _Docker.get().images.get(name)

    @classmethod
    def ls(cls, filter=None) -> typing.List[ImageType]:
        return _Docker.get().images.list(f"{PREFIX}_{filter or '*'}")

    @classmethod
    def delete(cls, tag):
        _Docker.get().images.remove(image=tag)

    @classmethod
    def create(cls, tag, path) -> ImageType:
        return _Docker.get().images.build(path=path, tag=tag, rm=True)


def add_prefix(name: str) -> str:
    if name.startswith(PREFIX):
        return name
    return f"{PREFIX}_{name}"


def remove_prefix(name: str) -> str:
    if name.startswith(PREFIX):
        return name[len(PREFIX) + 1 :]
    return name


class Image:
    def __init__(self, name: str = None, tag: str = None, ident: str = None):
        with logging.LogCall(__file__, "__init__", self.__class__):
            if ident:
                (name, tag) = ident.split(":")
                name = remove_prefix(name)
            if not (name and tag):
                raise ValueError("name and tag need to be specified")
            self.tag = tag
            self.name = name
            self.image_name = add_prefix(name)

    def get_ident(self) -> str:
        with logging.LogCall(__file__, "get_ident", self.__class__):
            return f"{self.image_name}:{self.tag}"

    @classmethod
    def ls(cls, filter=None) -> ImageType:
        with logging.LogCall(__file__, "ls", cls):
            return _Image.ls()

    def get_container(self) -> typing.List[ContainerType]:
        with logging.LogCall(__file__, "get_container", self.__class__):
            return Container.get_by_image(self)

    def exists(self) -> typing.Union[ImageType, None]:
        with logging.LogCall(__file__, "exists", self.__class__):
            try:
                return _Image.get(self.get_ident())
            except:
                return None

    def delete(self) -> bool:
        with logging.LogCall(__file__, "delete", self.__class__):
            with LockHandler.get("docker"):
                if not self.exists():
                    return False
                for c in self.get_container():
                    c.remove()
                _Image.delete(self.get_ident())
                return True

    def stop(self):
        with logging.LogCall(__file__, "stop", self.__class__):
            for c in self.get_container():
                c.stop()

    def start(self):
        with logging.LogCall(__file__, "start", self.__class__):
            for c in self.get_container():
                c.start()

    def create(self, directory: str) -> bool:
        with logging.LogCall(__file__, "create", self.__class__):
            with LockHandler.get("docker"):
                if self.exists():
                    return False
                _plugindir = os.path.join(directory, "container")
                _Image.create(self.get_ident(), _plugindir)
                return True


class Container:
    class State:
        EXITED = "exited"
        RUNNING = "running"
        RESTARTING = "restarting"
        PAUSED = "paused"

    def __init__(self, name: str = None, ident: str = None):
        with logging.LogCall(__file__, "__init__", self.__class__):
            if ident:
                name = remove_prefix(ident)
            if not name:
                raise ValueError("name needs to be specified")
            self.name = name
            self.container_name = self._get_name(name)

    def get_ident(self) -> str:
        return self.container_name

    @classmethod
    def get_by_image(cls, image: Image):
        with logging.LogCall(__file__, "get_by_image", cls):
            return _Container.by_image(image.get_ident())

    @classmethod
    def _get_name(cls, plugin_name: str) -> str:
        with logging.LogCall(__file__, "_get_name", cls):
            return f"{PREFIX}_{plugin_name}"

    @classmethod
    def ls(cls, filter: str = None):
        with logging.LogCall(__file__, "ls", cls):
            return _Container.ls(filter)

    def exists(self) -> typing.Union[ContainerType, None]:
        with logging.LogCall(__file__, "exists", self.__class__):
            try:
                return _Container.get(self.get_ident())
            except:
                return None

    def delete(self) -> bool:
        with logging.LogCall(__file__, "delete", self.__class__):
            with LockHandler.get("docker"):
                _Container.delete(self.get_ident())

    def create(self, image: Image) -> bool:
        with logging.LogCall(__file__, "create", self.__class__):
            with LockHandler.get("docker"):
                if self.exists():
                    return False
                _Container.create(
                    image.get_ident(), self.get_ident(), DOCKER_NETWORK,
                )
                return True

    def start(self) -> bool:
        with logging.LogCall(__file__, "start", self.__class__):
            with LockHandler.get("docker"):
                cnt = self.exists()
                if not cnt:
                    return False
                if cnt.status in (self.State.RUNNING, self.State.RESTARTING):
                    return False
                _Container.start(self.get_ident())
                return True

    def stop(self) -> bool:
        with logging.LogCall(__file__, "stop", self.__class__):
            with LockHandler.get("docker"):
                cnt = self.exists()
                if cnt.status == self.State.EXITED:
                    return False
            _Container.stop(self.get_ident())
            return True

    def is_running(self) -> bool:
        with logging.LogCall(__file__, "is_running", self.__class__):
            data = self.exists()
            if data:
                return data.status == self.State.RUNNING
            return False

    def logs(self) -> str:
        with logging.LogCall(__file__, "logs", self.__class__):
            container = self.exists()
            if not container:
                return None
            return container.logs(tail=1000)
