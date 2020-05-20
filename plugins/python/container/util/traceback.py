import traceback
import collections

def get(exception: Exception) -> dict:
    Traceback = collections.namedtuple('Traceback', ("file", "line", "func", "code"))
    return {
        "class": exception.__class__.__name__,
        "msg": str(exception),
        "tb": tuple({"index":i, **Traceback(*data)._asdict()} for (i, data) in enumerate(traceback.extract_tb(exception.__traceback__))),
    }
