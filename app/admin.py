import json
import re
import uuid
import typing
import enum
import itertools
import os

import django
import django.http
import django.shortcuts
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import get_plugin_list
from .models import Plugin, Setting, Docker
from .util import docker, log as logging, exception, format

admin.site.site_title = "Server Code Test"
admin.site.site_header = "Server Code Test - Admin"
admin.site.unregister(Group)


class CustomAdminList:
    class Column:
        class Type(enum.IntEnum):
            ANY = 0
            BOOL = 1
            FUNCTION = 2

        def __init__(
            self, name: str, key: str, *, is_bool=False, is_fn=False, type=None
        ):
            if is_bool:
                type = self.Type.BOOL
            elif is_fn:
                type = self.Type.FUNCTION
            if not type:
                type = self.Type.ANY
            self.name = name
            self.key = key
            self.type = type

        def data(self, data: "CustomAdminList"):
            attrib = getattr(data, self.key)
            if self.type == self.Type.FUNCTION:
                return attrib()
            return admin.utils.display_for_value(
                attrib, "", self.type == self.Type.BOOL
            )

    columns = tuple()

    @classmethod
    def create_button(cls, name: str, value: str, text, disabled=False):
        return django.utils.html.format_html(
            '<button {} name="{}" value="{}">{}</button>',
            "disabled" if disabled else "",
            name,
            value,
            text,
        )

    @classmethod
    def head(cls):
        return map(lambda entry: entry.name, cls.columns)

    def data(self):
        return map(lambda entry: entry.data(self), self.columns)


@admin.register(Plugin)
class PluginAdmin(admin.ModelAdmin):
    change_list_template = "admin.docker.list.html"

    class Entry(CustomAdminList):
        columns = (
            CustomAdminList.Column(_("title.name"), "name"),
            CustomAdminList.Column(_("title.version"), "version"),
            CustomAdminList.Column(_("title.state"), "tstate", is_fn=True),
            CustomAdminList.Column(_("title.active"), "active", is_bool=True),
            CustomAdminList.Column(_("title.actions"), "add_buttons", is_fn=True),
        )
        def tstate(self):
            icon = admin.utils.display_for_value(self.handle.State.NONE!=self.state, "", True)
            prefix = "*" if self.handle.State.UPDATED==self.state else ""
            postfix = f" v{self.handle.version}" if self.handle.State.UPDATED==self.state else ""
            return django.utils.html.format_html(f"{prefix}{icon}{postfix} (PID: {os.getpid()})")

        def __init__(self, uid, handle, db):
            self.id = uid
            self.handle = handle
            self.name = handle.info.name
            self.version = handle.info.version
            self.state = handle.get_state()
            self.active = db.active if db else False

        @classmethod
        def create_button(cls, *args, **kwargs):
            return super().create_button("plugin_action", *args, **kwargs)

        def add_buttons(self):
            value = f"%s {self.id}"
            if self.state == self.handle.State.NONE:
                load = self.create_button(value % "load", _("action.load"))
            else:
                load = self.create_button(value % "reload", _("action.reload"))
            if self.active:
                state = self.create_button(value % "disable", _("action.disable"))
            else:
                state = self.create_button(value % "enable", _("action.enable"))
            return load + state

    _messages = (
        {
            "load": _("plugin.message.load"),  # "{} loaded",
            "reload": _("plugin.message.reload"),  # "{} reloaded",
            "disable": _("plugin.message.disable"),  # "{} disabled",
            "enable": _("plugin.message.enable"),  # "{} enabled",
        },
        {
            "load": _("plugin.error.load"),  # "{} loaded",
            "reload": _("plugin.error.reload"),  # "{} reloaded",
            "disable": _("plugin.error.disable"),  # "{} disabled",
            "enable": _("plugin.error.enable"),  # "{} enabled",
        },
    )
    # https://gist.github.com/hakib/ec462baef03a6146654e4c095142b5eb
    def changelist_view(self, request, *args, **kwargs):
        with logging.LogCall(__file__, "changelist_view", self.__class__):
            if "plugin_action" in request.POST:
                try:
                    (action, uid) = re.match(
                        "(load|reload|disable|enable) (.+)",
                        request.POST["plugin_action"],
                    ).groups()
                    if action in ("load", "reload"):
                        get_plugin_list()[uid].load()
                    if action in ("disable", "enable"):
                        if action == "enable":
                            Plugin.enable(uid)
                        else:
                            Plugin.disable(uid)
                    self.message_user(
                        request, self._messages[0].get(action, "{}").format(uid)
                    )
                except Exception as e:
                    exception.Traceback(e).log()
                    self.message_user(
                        request,
                        f"{self._messages[1].get(action, '{}').format(uid)}: <pre>{format.to_html(str(exception.Traceback(e)))}<pre>",
                        level=messages.ERROR,
                        extra_tags="safe",
                    )
                finally:
                    return redirect(request.build_absolute_uri())
            response = super().changelist_view(request, *args, **kwargs)
            try:
                qs = response.context_data["cl"].queryset
            except (AttributeError, KeyError):
                return response

            entries = map(
                lambda plugin: self.Entry(*plugin, qs.filter(pk=plugin[0]).first()),
                get_plugin_list().load(True),
            )

            response.context_data["data_head"] = self.Entry.head()
            response.context_data["data"] = map(lambda entry: entry.data(), entries)
            return response

    def has_view_permission(self, *args, **kwargs) -> bool:
        with logging.LogCall(__file__, "has_view_permission", self.__class__):
            return True

    def has_add_permission(self, *args, **kwargs) -> bool:
        with logging.LogCall(__file__, "has_add_permission", self.__class__):
            return False

    def has_change_permission(self, *args, **kwargs) -> bool:
        with logging.LogCall(__file__, "has_change_permission", self.__class__):
            return False

    def has_module_permission(self, *args, **kwargs) -> bool:
        with logging.LogCall(__file__, "has_module_permission", self.__class__):
            return True

    def has_delete_permission(self, *args, **kwargs) -> bool:
        with logging.LogCall(__file__, "has_delete_permission", self.__class__):
            return False


class PluginChoice(django.forms.ModelChoiceField):
    def label_from_instance(self, obj):
        lst = get_plugin_list()
        try:
            return lst[obj.uid].info.name
        except:
            return obj.uid


class SettingForm(django.forms.ModelForm):
    class Meta:
        model = Setting
        exclude = []

    class Media:
        js = ("pluginLoader.js", "helper.js", "https://code.jquery.com/jquery-3.4.1.min.js")
        css = { "all":("custom.css",)}


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    form = SettingForm
    readonly_fields = ("token", "date")
    fieldsets = (
        (_("general"), {"fields": ("name", "plugin", "token", "date")}),
        (_("readonly"), {"fields": ("settings",)}),
    )
    list_display = ("name", "token", "plugin", "date")
    list_filter = ("name", "plugin", "date")
    change_form_template = 'plugin.setting.change_view.html'

    def changeform_view(self, request: WSGIRequest, object_id=None, form_url='', extra_context=None):
        Plugin.clear()  # remove deleted plugins from table
        if object_id != None:
            print(object_id)
            extra_context = {"setting_id":object_id}
        return super().changeform_view(request, object_id, form_url, extra_context)

    def formfield_for_foreignkey(self, db_field, *args, **kwargs):
        if db_field.name == "plugin":
            return PluginChoice(
                queryset=Plugin.objects.filter(active=True)  # pylint: disable=no-member
            )
        return super().formfield_for_foreignkey(db_field, *args, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            django.urls.path(
                "form/<uuid:settings>/<slug:plugin>/",
                admin.site.admin_view(self.get_plugin_form),
            ),                
        ]
        return my_urls + urls

    def get_plugin_form(self, request: WSGIRequest, plugin: str, settings: uuid.UUID):
        _plugin = get_plugin_list()[plugin]
        if not _plugin:
            return django.http.HttpResponseNotFound()
        # pylint: disable=no-member
        data = Setting.objects.filter(token=settings).first()
        # pylint: enable=no-member

        context = {
            "form": _plugin.get()
            .Settings(json.loads(data.settings) if data else {})
            .to_form(),
            "name": _("plugin.settings"),
            "id": "plugin_specific_settings",
        }
        return django.shortcuts.render(request, "plugin.settings.html", context)

    def has_change_permission(
        self, request: WSGIRequest, obj: Setting = None, *args, **kwargs
    ):
        try:
            get_plugin_list()[obj.plugin.uid]
            return obj.plugin.active
        except:
            pass
        return True

    def save_model(
        self, request: WSGIRequest, obj: Setting, form: SettingForm, change: bool
    ):
        _plugin = get_plugin_list()[str(form.cleaned_data["plugin"])]
        if not _plugin:
            return django.http.HttpResponseNotFound()
        f = _plugin.get().Settings().from_form(request.POST)
        obj.data = "{}"
        obj.settings = json.dumps(f.serialize())
        obj.date = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Docker)
class DockerAdmin(admin.ModelAdmin):
    change_list_template = "admin.docker.list.html"
    _messages = (
        {
            "delete": _("docker.message.delete"),  # "{} loaded",
            "start": _("docker.message.start"),  # "{} reloaded",
            "stop": _("docker.message.stop"),  # "{} disabled",
        },
        {
            "delete": _("docker.error.delete"),  # "{} loaded",
            "start": _("docker.error.start"),  # "{} reloaded",
            "stop": _("docker.error.stop"),  # "{} disabled",
        },
    )

    class Entry(CustomAdminList):
        columns = (
            CustomAdminList.Column(_("title.name"), "name"),
            CustomAdminList.Column(_("title.docker.image"), "image"),
            CustomAdminList.Column(_("title.state"), "state"),
            CustomAdminList.Column(_("title.docker.container"), "container", is_bool=True),
            CustomAdminList.Column(_("title.actions"), "add_buttons", is_fn=True),
        )

        @classmethod
        def from_image(cls, image, tags):
            return map(
                lambda tag: cls(tag, tag, "", "used" if tag in tags else "", False),
                image.tags,
            )

        @classmethod
        def from_container(cls, data):
            image = data.attrs["Config"]["Image"]
            return cls(data.name, data.name, image, data.status, True)

        def __init__(self, id, name, image, state, container):
            self.id = id
            self.name = name
            self.image = image
            self.state = state
            self.container = container

        @classmethod
        def create_button(cls, *args, **kwargs):
            return super().create_button("docker_action", *args, **kwargs)

        def add_buttons(self):
            running = self.state in (docker.Container.State.RUNNING, "used")
            value = f"%s {'c' if self.container else 'i'} {self.id}"
            startable = self.container and running

            start = self.create_button(value % "start", _("action.start"), startable)
            stop = self.create_button(value % "stop", _("action.stop"), not running)
            delete = self.create_button(value % "delete", _("action.delete"), running)
            btns = start + stop + delete
            if self.container:
                logs = self.create_button(value % "logs", _("action.logs"), False)
                return btns + logs
            return btns

    # https://gist.github.com/hakib/ec462baef03a6146654e4c095142b5eb
    def changelist_view(self, request, *args, **kwargs):
        with logging.LogCall(__file__, "changelist_view", self.__class__):
            if "docker_action" in request.POST:
                try:
                    (action, typ, id) = re.match(
                        r"(start|stop|delete|logs) (c|i) ([a-zA-Z0-9-_]+)", request.POST["docker_action"]
                    ).groups()
                    typ = docker.Container if typ == "c" else docker.Image
                    instance = typ(ident=id)
                    res = getattr(instance, action)()
                    if action=="logs" and res:
                        response = django.http.HttpResponse(res, content_type='application/text')
                        response['Content-Disposition'] = f'attachment; filename={id}.log'
                        return response
                    self.message_user(
                        request, self._messages[0].get(action, "{}").format(id)
                    )
                except Exception as e:
                    exception.Traceback(e).log()
                    self.message_user(
                        request,
                        f"{self._messages[1].get(action, '{}').format(id)}: <pre>{format.to_html(str(exception.Traceback(e)))}<pre>",
                        level=messages.ERROR,
                        extra_tags="safe",
                    )
                return redirect(request.build_absolute_uri())
            response = super().changelist_view(request, *args, **kwargs)

            # get containerlist
            container = tuple(map(self.Entry.from_container, docker.Container.ls()))
            used_containe = filter(lambda c: c.state==docker.Container.State.RUNNING, container)
            used_images = set(map(lambda entry: entry.image, used_containe))

            # get imagelist
            fn = lambda img: self.Entry.from_image(img, used_images)
            images = tuple(map(fn, docker.Image.ls()))  # tuple of maps

            # create entry list
            entries = itertools.chain(*images, container)

            response.context_data["data_head"] = self.Entry.head()
            response.context_data["data"] = map(lambda entry: entry.data(), entries)
            return response

    def has_view_permission(self, *args, **kwargs) -> bool:
        with logging.LogCall(__file__, "has_view_permission", self.__class__):
            return True

    def has_add_permission(self, *args, **kwargs) -> bool:
        with logging.LogCall(__file__, "has_add_permission", self.__class__):
            return False

    def has_change_permission(self, *args, **kwargs) -> bool:
        with logging.LogCall(__file__, "has_change_permission", self.__class__):
            return False

    def has_module_permission(self, *args, **kwargs) -> bool:
        with logging.LogCall(__file__, "has_module_permission", self.__class__):
            return True

    def has_delete_permission(self, *args, **kwargs) -> bool:
        with logging.LogCall(__file__, "has_delete_permission", self.__class__):
            return False
