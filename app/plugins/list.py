import typing
import sys
import os

from .handle import Handle
from .info import Info
from ..util import log as logging, exception

PluginList = typing.Dict[str, Handle]


class List:
    def __init__(self, path: str):
        with logging.LogCall(__file__, "__init__", self.__class__):
            sys.path.append(path)
            self.path = path
            self.plugins: PluginList = {}
            self.loaded = False

    def load(self, force=False):
        with logging.LogCall(__file__, "load", self.__class__):
            if self.loaded and not force:
                return self
            self.loaded = True

            new: dict = {}
            exist: list = []

            for path in os.listdir(self.path):
                _path = os.path.join(self.path, path)
                try:
                    info = Info.from_file(os.path.join(_path, "plugin.json"))
                except Exception as e:
                    exception.Traceback(e).log()
                    continue
                # don't reload existing plugins
                if (pl := self.plugins.get(info.uid, None)) != None:
                    pl: Handle = pl
                    exist.append(info.uid)
                    if pl.info.version != info.version:
                        pl.update(info)
                    continue
                handle = Handle(_path, info)
                new[info.uid] = handle
            # remove deleted plugins
            for key in set(self.plugins.keys()).difference(exist):
                self.plugins.pop(key, None)

            # insert new plugins
            self.plugins.update(new)
            return self

    def get(self) -> PluginList:
        with logging.LogCall(__file__, "get", self.__class__):
            self.load()
            return self.plugins

    def __getitem__(self, key) -> typing.Union[Handle, None]:
        with logging.LogCall(__file__, "__getitem__", self.__class__):
            self.load()
            try:
                return self.plugins[key]
            except Exception:
                return None

    def __iter__(self):
        with logging.LogCall(__file__, "__iter__", self.__class__):
            self.load()
            return iter(self.plugins.items())

