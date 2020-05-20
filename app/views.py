import json
import uuid

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from . import get_plugin_list
from .models import Setting
from .util import timeout, log as logging


class ErrorView:
    def __init__(self, key, text, code=500):
        self.error = key
        self.message = text
        self.code = code

    def to_response(self):
        res = HttpResponse()
        res.status_code = self.code
        data = {"error": {"key": self.error, "text": self.message}}
        res.content = json.dumps(data)
        return res


def _timeout(*args, **kwargs):
    return ErrorView("timeout", "a timeout occured", 500).to_response()


@method_decorator(csrf_exempt, name="dispatch")
class API(View):
    allowed_methods = ["post", "options"]

    def options(self, *args, **kwargs):
        response = HttpResponse()
        response["allow"] = ",".join(self.allowed_methods)
        return response

    def dispatch(self, *args, **kwargs):
        res = super().dispatch(*args, **kwargs)
        if isinstance(res, HttpResponse):
            res["Access-Control-Allow-Origin"] = "*"
            res["Access-Control-Allow-Methods"] = "POST"
            res["Access-Control-Allow-Headers"] = "Content-Type"
        return res

    def http_method_not_allowed(self, request, *args, **kwargs):
        with logging.LogCall(__file__, "http_method_not_allowed", self.__class__):
            return ErrorView("method", "POST only", 405).to_response()

    @timeout.timeout(settings.TIMEOUT, _timeout)
    def post(self, request: WSGIRequest, token: uuid.UUID):
        with logging.LogCall(__file__, "post", self.__class__):
            try:
                db_setting = Setting.objects.get(  # pylint: disable=no-member
                    token=token, plugin__active=True
                )
            except:
                return ErrorView("disabled", "Plugin Disabled", 404).to_response()
            try:
                _plugin = get_plugin_list()[str(db_setting.plugin)]
                _plugin = _plugin.get()
            except:
                return ErrorView("disabled", "Plugin Disabled", 500).to_response()
            body = json.loads(request.body.decode("utf-8"))

            req = _plugin.Request(
                token=db_setting.token,
                version=str(db_setting.date),
                settings=json.loads(db_setting.settings),
                timeout=settings.TIMEOUT,
                body=body
            )
            response = _plugin.execute(req)
            res = HttpResponse()
            res.status_code = 500 if response.has_error() else 200
            res.content = json.dumps(response.serialize())
            return res


@csrf_exempt
def error_404(request: WSGIRequest):
    return ErrorView("malformed", "Malformed request...", 404).to_response()
