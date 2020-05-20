user = """
#import os

def sort(lst):
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if lst[i]>lst[j]:
                tmp = lst[j]
                lst[j] = lst[i]
                lst[i] = tmp
    return lst

def test_t1():
    assert sort([])==[]
    assert sort([1])==[1]
    assert sort([1,1])==[1,1]
    assert sort([1,2,3])==[1,2,3]
    assert sort([4,2,3])==[2,3,4]
    assert sort([]) == 1
"""

compare = """
set_function("sort")

def blackbox(lst):
    lst = sorted(lst)
    return lst

from hypothesis import given
import hypothesis.strategies as st

def sort(lst):
    return blackbox(lst)

@test(1)
@given(st.lists(st.integers()))
def test_random(fn, lst):
    assert sort(lst)==fn(lst)
    assert False

@test(1)
def test_1(fn):
    lst = [1,52,3]
    assert sort(lst)==fn(lst)

@check_args(5, "blubber1")
def test_2(lst, *args, **kwargs):
    print(3)
    assert len(lst)==0
"""