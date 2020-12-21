# Python 3 Plugin for ServerCodeTest
## Requirements
* docker

## Response
see ServerCodeTest docu.

## Plugin Settings
* Debug:
  * activates more detailed output. E.g. failed tests
* Execute Code:
  * user code will be executed
* Mark:
  * test code will be executed
* Print Mark Result:
  * Output of Mark will be printed. 
  * If this is disabled, the resulting score will still be added in the json response.
* Run Pytest:
  * user code will be executed by pytest
* Allowed usercode/mark code imports:
  * usable modules need to be added here

## Code grading

You may set the FUT (*given function*) using `set_function(name:str)`. This corresponds to using injection.
Alternatively, you may access functions submitted by the student in module user. In this case, injection is not needed.

### Decorators
* `test(points:Union[int,float]=0, description:str="")`
  * registers the following function as a test function.
  * injects the *given function* as first argument of the test function
* `test_no_inject(points:Union[int,float]=0, description:str="")`
  * registers the following function as a test function.
* `check_args(points:Union[int,float]=0, description:str="")`
  * registers the following function as an argument check function.
  * will be called for each call to the *given function* and injects the arguments of the calls.

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

## the variable names in the decorators `given` and `example` *must* match the parameter name of the test function.

@test_no_inject(points=2, description="Test 3")
@given(x=st.lists(st.integers()))
@example(x=[])
def test_3(x):
  assert sorted(x) == user.sort(x)

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
