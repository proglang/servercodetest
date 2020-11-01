import os
import sys
import json

sys.path[0] = os.path.abspath(os.getcwd())

delimiter = os.environ.get("DELIMITER")
del os.environ["DELIMITER"]

# pylint: disable=import-error
import sct_test
import sct_user
import sct_compare

# pylint: enable=import-error

setattr(sct_compare, "user", sct_user)
sct_test.Test.check(sct_user)
sct_test.CheckArgs.check(sct_user)


print(f"<{delimiter}>")
try:
    data = {}
    data["test"] = sct_test.Test.serialize()
    data["args"] = sct_test.CheckArgs.serialize()
    print(json.dumps(data))
except:
    raise
finally:
    print(f"</{delimiter}>")
