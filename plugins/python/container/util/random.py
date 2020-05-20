from string import ascii_uppercase as _ascii_uppercase
from random import choice as _choice


def string(stringLength=10):
    """Generate a random string of fixed length """
    # https://pynative.com/python-generate-random-string/
    letters = _ascii_uppercase
    return "".join(_choice(letters) for i in range(stringLength))
