import re
import util
import util.iterator
import json
from .struct import Output, CyclomaticComplexity, Raw


def _get(method: str, _dir: str) -> str:
    try:
        data = json.loads(util.Popen("radon", method, "-j", _dir).data)
        for key, file_data in data.items():
            if file_data.get("error", False):
                del data[key]
        return data
    except:
        return {}


def get_cc(_dir):
    data = _get("cc", _dir)
    res = CyclomaticComplexity()
    for (_, entries) in data.items():
        for entry in entries:
            fn = entry.get("name", 0)
            type = entry.get("type", 0)
            complexity = entry.get("complexity", 0)
            rank = entry.get("rank", 0)
            res.add(fn, type, rank, complexity)
        break
    return res


def get_raw(_dir):
    data = _get("raw", _dir)
    res = Raw()
    for (_, entry) in data.items():
        loc = entry.get("loc", 0)
        sloc = entry.get("sloc", 0)
        lloc = entry.get("lloc", 0)
        res.set(loc, sloc, lloc)
        break
    return res


def get(_dir, global_settings):
    output = Output()
    output.raw = get_raw(_dir)
    output.cyclomatic_complexity = get_cc(_dir)
    return output.serialize()
