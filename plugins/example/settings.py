# pylint: disable=import-error
from app.plugins.plugin import Settings as BaseSettings

# pylint: enable=import-error
from django import forms

class Form(BaseSettings.Form):
    debug = forms.BooleanField(label="Debug", required=False)
    exec = forms.BooleanField(label="Execute Code", required=False)

class Settings(BaseSettings):
    Form = Form

    def __init__(self, data: dict = {}):
        if not isinstance(data, dict):
            data = {}
        self.debug = data.get("debug", False)
        self.exec = data.get("exec", False)

########## Not required since no transformations are needed.
#    def get_form_data(self):
#        ret = {
#            "debug": self.debug,
#            "exec": self.exec.run,
#        }
#        return ret


########## This is always required. SANITIZE YOUR INPUTS HERE!!!
    def from_form_data(self, data: dict = {}):
        self.debug = data["debug"]
        self.exec = data["exec"]

