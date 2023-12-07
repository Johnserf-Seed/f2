mode_function_map = {}


def mode_handler(mode_name):
    def decorator(function):
        mode_function_map[mode_name] = function
        return function

    return decorator
