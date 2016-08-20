"""Side utilities module for the Metador project."""
import timeit


def time_decorator(org_function, ):
    def actual_decorator(*args, **kwargs):
        timeit_start_time = timeit.default_timer()
        result = org_function(*args, **kwargs)
        print(timeit.default_timer() - timeit_start_time), "seconds"
        return result

    return actual_decorator
