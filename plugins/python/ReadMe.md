# Python 3 Plugin for ServerCodeTest
## Requirements
* docker

## Response
see ServerCodeTest docu.

## Code grading
### Decorators
* `test(points:Union[int,float]=0, description:str="")`
  * registers the following function as a test function.
  * injects the *given function* as first argument
* `test_no_inject(points:Union[int,float]=0, description:str="")`
  * registers the following function as a test function.
* `check_args(points:Union[int,float]=0, description:str="")`
  * registers the following function as an argument check function.
  * will be called for each call to the *given function* and injects the arguments of the calls.

*given function*: function set with `set_function(name:str)`

### Example
**Student Code:**
```python
def sort(lst: list):
    return sorted(lst)
    
def test_1():
  assert sort([]) == []

def test_2():
  assert sort([2,1]) == [1,2]
```
unittests need to be prefixed with `test_`

**Grading code**
```python
set_function("sort") 

###
@test(points=1, description="Test 1")
def test_1(fn):
  assert [] == fn([])

###
@test(points=1, description="Test 2")
def test_2(fn):
  assert [] == user.sort([])

###
from hypothesis import given, example
import hypothesis.strategies as st

@test_no_inject(points=2, description="Test 3")
@given(x=st.lists(st.integers()))
@example(x=[])
def test_3(args):
  assert sorted(args) == user.sort(args)

##################################
@check_args(points=1, description="CA 1")
def ca_1(lst:list, *args, **args):
  assert lst==[]

###
@check_args(points=1, description="CA 2")
def ca_2(lst:list, *args, **args):
  assert len(lst) == 1
```
As seen above, the student code will be implicitly imported as module `user`.

If `check_args` is used a function needs to be set with `set_function`.

## dev notes
### updates:
* don't forget to increase version in plugin.json
