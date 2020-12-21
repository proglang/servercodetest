"""This file defines functions and decorators to mark code.
Functions:
- set_function(name)
Decorators:
- test
- test_no_inject
- check_args

Dev Note:
All decorators and functions must be imported from the file.
=> plugin.py filter_source 
"""

import itertools

def set_function(name:str):
    Hook.init(name)


def test(points:int=0, description:str="", inject_fn:bool=True):
    """
Add Testfunction:
- points: number of points if test is successful
- description: Description of the test
- injects function as first argument if a function was set with set function

Example:
@test(points=1, description="test 1")
def test_1(fn):
    assert False

@test(points=2, description="test 2")
def test_2(fn):
    assert True
"""
    return Test.decorator(description, points, not inject_fn)

def test_no_inject(points:int=0, description:str=""):
    """Same as test but doesn't inject function as first argument
    """ 
    return test(points, description, False)


def check_args(points:int=0, description:str=""):
    """
Checks if a function was called with specific arguments:
- set_function needs to be called to use this decorator
- points: number of points if test is successful
- description: Description of the test
- injects the arguments of all calls to the specified function as arguments

Example:
set_function("name")

@check_args(points=1, description="test 1")
def test_1(arg1, arg2, *args, **kwargs):
    assert False

@check_args(points=2, description="test 2")
def test_2(arg1, arg2, *args, **kwargs):
    assert True
"""
    return CheckArgs.decorator(description, points)


class Hook:
    name = ""

    @classmethod
    def init(cls, name:str):
        cls.name = name if isinstance(name, str) else ""

    @classmethod
    def get_function(cls, module):
        try:
            return getattr(module, cls.name)
        except:
            return None

    def __init__(self, module):
        self.module = module
        self.args = []
        self.original_fn = None

    def _hook_fn(self, *args, **kwargs):
        self.args.append((args, kwargs))
        return self.original_fn(*args, **kwargs)

    def get(self):
        args = self.args
        args.sort()
        return tuple(k for k, _ in itertools.groupby(args))

    def __enter__(self):
        if (fn := self.get_function(self.module)) :
            self.original_fn = fn
            setattr(self.module, self.name, self._hook_fn)
        return self

    def __exit__(self, error, message, traceback):
        if self.original_fn != None:
            setattr(self.module, self.name, self.original_fn)
        if error:
            raise


class Base:
    class Entry:
        def __init__(self, name, fn, description, points):
            self.name = name
            self.fn = fn
            self.description = description
            self.points = points
    
    registered = None
    completed = None

    @classmethod
    def init(cls):
        if cls.registered == None:
            cls.registered = []
        if cls.completed == None:
            cls.completed = []

    @classmethod
    def register(cls, name, fn, description, points):
        cls.init()
        cls.registered.append(cls.Entry(name, fn, description, points))

    @classmethod
    def decorator(cls, description="", points=0, no_args=False):
        def fn_wrapper(fn):
            def wrapper(*args, **kwargs):
                if no_args:
                    return fn()
                else:
                    return fn(*args, **kwargs)
            cls.register(fn.__name__, wrapper, description, points)
            return wrapper

        return fn_wrapper

    @classmethod
    def check(cls, *args, **kwargs):
        cls.init()
        _index = []
        for (index, entry) in enumerate(cls.registered):
            try:
                entry.fn(*args, **kwargs)
                cls.completed.append(entry)
                _index.append(index)
            except AssertionError:
                pass
            except Exception as e:
                print(e) #TODO: write Exception in useful text
        _index = sorted(_index, reverse=True)
        for index in _index:
            del cls.registered[index]

    @classmethod
    def _serialize(cls, obj):
        if obj==None:
            return tuple()
        return tuple( (entry.name, entry.description, entry.points) for entry in obj)

    @classmethod
    def serialize(cls):
        ret = {}
        ret["reg"] = cls._serialize(cls.registered)
        ret["suc"] = cls._serialize(cls.completed)
        return ret


    @classmethod
    def get(cls):
        cls.init()


def get_tests(module):
    return (
        getattr(module, name)
        for name in dir(module)
        if name.lower().startswith("test_")
    )


class CheckArgs(Base):
    @classmethod
    def check(cls, module):
        hook = Hook(module)
        with hook:
            for fn in get_tests(module):
                try:
                    fn()
                except:
                    pass
        for (args, kwargs) in hook.get():
            super().check(*args, *kwargs)


class Test(Base):
    @classmethod
    def check(cls, module):
        fn = Hook.get_function(module)
        super().check(fn)

if __name__=="__main__":
    import sys
    current = sys.modules[__name__]
    def fn(args):
        return 0
    def test_fn():
        fn(1)
        fn(2)
        fn(3)
    @test(1, "test", False)
    def t1():
        pass
    @check_args(2, "cha")
    def t2(args):
        pass
    set_function("fn")
    Test.check(current)
    print(Test.serialize())
    CheckArgs.check(current)
    print(CheckArgs.serialize())
