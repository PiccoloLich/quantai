#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
decorators to python function

@author: piccolo
"""


from functools import wraps
from timeit import default_timer as timer

def logit(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        print(func.__name__ + " was called")
        return func(*args, **kwargs)
    return with_logging

def append_time(func):
    @wraps(func)
    def timed_func(*args, **kwargs):
        start = timer()
        result = func(*args, **kwargs)
        end = timer()
        time_diff = end - start
        return result, time_diff
    return timed_func
        
if __name__ == "__main__":

    @logit
    def addition_func(x):
        """Do some math."""
        return x + x

    @append_time
    def addition_func2(x):
        """Do some math."""
        return x + x

    result = addition_func(4)
    # Output: addition_func was called

    result2 = addition_func2(3)
    print(result2)
