import logging
from functools import wraps
from time import perf_counter
from typing import Any, Callable

logger = logging.getLogger(__name__)


def time_function(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        value = func(*args, **kwargs)
        end = perf_counter()
        runtime = end - start
        logger.info("function %s ran in %.2f seconds", func.__name__, runtime)
        return value

    return wrapper
