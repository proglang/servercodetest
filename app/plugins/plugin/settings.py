import django
import json

from app.util import log as logging


class Form(django.forms.Form):
    """class which specifies form fields.
    for details how to build a form:
    https://docs.djangoproject.com/en/3.0/topics/forms/
    """
    pass

class Settings:
    """This class contains methods to help with Settings.
    The Form Attribute MUST be a class which implements a django Form.
    """
    Form = Form

    def __init__(self, data: dict = {}):
        """specify your fields here"""
        pass

    def get_form_data(self) -> dict:
        """translate your settings structure to your forms data structure"""
        with logging.LogCall(__file__, "get_form_data", self.__class__):
            return self.serialize()

    def from_form_data(self, data: dict = {}):
        """translate your form data structure to your settings structure"""
        with logging.LogCall(__file__, "from_form_data", self.__class__):
            pass

    ##### DO NOT OVERWRITE METHODS BELOW #####
    def serialize(self) -> dict:
        with logging.LogCall(__file__, "serialize", self.__class__):
            ret = {}
            for k, v in self.__dict__.items():
                if hasattr(v, "serialize"):
                    ret[k] = v.serialize()
                else:
                    ret[k] = v
            return ret

    def to_form(self):
        return self.Form(self.get_form_data())

    def from_form(self, data: dict):
        form = self.Form(data)
        form.full_clean()
        self.from_form_data(form.cleaned_data)
        return self
