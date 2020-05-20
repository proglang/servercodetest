from . import plugins


def get_plugin_list() -> plugins.List:
    from django.apps import apps

    return apps.get_app_config("app").plugin_list
