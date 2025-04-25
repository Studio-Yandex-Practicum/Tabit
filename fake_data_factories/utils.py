from functools import wraps

from termcolor import cprint

from config.constants.fake_data_factories import ColorCPrint


def start_and_end(name: str = '', color: str = ColorCPrint.yellow):
    def decorator(func):
        wraps(func)

        async def wrapper(*args, **kwargs):
            cprint(f'Начало работы {name}...', color)
            result = await func(*args, **kwargs)
            cprint(f'...конец работы {name}.', color)
            return result

        return wrapper

    return decorator
