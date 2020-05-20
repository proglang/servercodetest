import os
import importlib
import enum

from .info import Info
from .plugin import Plugin
from .exception import PluginException


class Handle:
    class State(enum.IntEnum):
        NONE = 0
        LOADED = 1
        UPDATED = 2

    def __init__(self, path: str, info: Info):
        self.path = os.path.abspath(path)
        self.info = info
        self.module = None
        self.plugin = None
        self.state = self.State.NONE
        self.version = None

    def get_state(self) -> "Handle.State":
        return self.state

    def get(self) -> Plugin:
        if not self.get_state() == self.State.LOADED:
            self.load()
        return self.plugin

    def update(self, info: Info):
        self.info = info
        if self.get_state() == self.State.LOADED:
            self.state = self.State.UPDATED

    def _reload(self):
        return importlib.reload(self.module)

    def _load(self):
        return importlib.import_module(os.path.split(self.path)[1])

    def load(self):
        self.module = self._reload() if self.module else self._load()
        try:
            if not isinstance(self.module.Plugin, type):
                raise PluginException("plugin.Plugin is not a type!")
            if not issubclass(self.module.Plugin, Plugin):
                raise PluginException("plugin.Plugin needs to be a subclass of Plugin")
            self.plugin = self.module.Plugin(self.info, self.path)
            self.state = self.State.LOADED
            self.version = self.info.version
        except:
            raise

