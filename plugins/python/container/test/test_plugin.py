import plugin
from .testdata import user, compare
import json

SETTINGS = {
    "exec": {"run": True, "mark": True, "pytest": True},
    "sandbox": {
        "user": tuple(),
        "test": ({"module": "hypothesis", "allowed": []}, {"module": "hypothesis.strategies", "allowed": []}),
    },
}

SENT = {"test": "", "blub": compare, "code":user}


def test_plugin():
    pl = plugin.Plugin()
    pl.setSettings(0, SETTINGS)
    data = pl.exec(SENT)
    print(data)
    assert False
