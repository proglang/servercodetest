import os

def to_int(num, default, min=None, max=None) -> int:
    try:
        num = int(num)
    except:
        num = default
    if min and num < min:
        return min
    if max and num > max:
        return max
    return num

def to_bool(value, default: bool=False) -> bool:
    if value==None:
        return default
    return value=="1"

def env(key, default=None,*,delete=False):
    val = os.getenv(key, default)
    if delete:
        try:
            del os.environ[key]
        except:
            pass
    return val

def etob(key, default:bool=False):
    return to_bool(env(key), default)

def etoi(key, default, min=None, max=None):
    return to_int(env(key), default, min, max)
