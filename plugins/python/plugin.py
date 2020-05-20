# pylint: disable=import-error
from app.plugins.plugin import Plugin
from .executor import Executor
from .settings import Settings
# pylint: enable=import-error

class PythonPlugin(Plugin):
    Settings = Settings
    Executor = Executor
