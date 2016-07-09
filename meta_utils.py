"""Side utilities module for the Metador project."""
import timeit


class ClassTimeitWrapper(object):
    """Decorator for time measurement in methods. """
    def __init__(self, org_function):
        self.org_function = org_function

    def __call__(self, *args, **kwargs):
        timeit_start_time = timeit.default_timer()
        self.org_function(self, *args, **kwargs)
        print(timeit.default_timer() - timeit_start_time)


class FuncTimeitWrapper(object):
    """Decorator for time measurement in functions. """
    def __init__(self, org_function):
        self.org_function = org_function

    def __call__(self, *args, **kwargs):
        timeit_start_time = timeit.default_timer()
        self.org_function(*args, **kwargs)
        print(timeit.default_timer() - timeit_start_time)
