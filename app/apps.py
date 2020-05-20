from django.apps import AppConfig as _AppConfig
from . import plugins
from django.conf import settings


class AppConfig(_AppConfig):
    name = "app"

    def ready(self):
        super().ready()
        self.plugin_list = plugins.List(settings.PLUGIN_DIR)
