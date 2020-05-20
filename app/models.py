import uuid
import typing

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import get_plugin_list


class Plugin(models.Model):
    class Meta:
        verbose_name = _("plugin")
        verbose_name_plural = _("plugins")

    uid = models.CharField(max_length=200, primary_key=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        lst = get_plugin_list()
        try:
            return lst[uid].info.name
        except:
            return self.uid

    @classmethod
    def clear(cls):
        entries = (uid for (uid, _) in get_plugin_list())
        try:
            cls.objects.all().exclude(pk__in=entries).delete()
        except:
            pass

    @classmethod
    def is_active(cls, uid: str) -> typing.Union["Plugin", None]:
        try:
            return cls.objects.get(uid=uid)
        except:
            return None

    @classmethod
    def enable(cls, uid: str):
        try:
            entry = cls(uid=uid, active=True)
            entry.save()
        except:
            pass

    @classmethod
    def disable(cls, uid: str):
        try:
            entry = cls.objects.get(uid=uid)
        except:
            return
        try:
            entry.delete()
        except:
            entry.active = False
            entry.save()


class Setting(models.Model):
    class Meta:
        verbose_name = _("setting")
        verbose_name_plural = _("settings")

    plugin = models.ForeignKey(
        Plugin, on_delete=models.PROTECT, verbose_name=_("plugin.name")
    )
    name = models.CharField(
        max_length=200, verbose_name=_("setting.name"), default="default"
    )
    date = models.DateTimeField(verbose_name=_("date"), auto_now_add=True)
    settings = models.TextField(blank=True)
    token = models.UUIDField(
        verbose_name=_("setting.token"),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    def __str__(self):
        return self.name


class Docker(Setting):
    class Meta:
        proxy = True
        verbose_name = "Docker"
        verbose_name_plural = "Docker"


