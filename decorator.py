import logging
import time
from functools import wraps
from typing import Callable

logger = logging.getLogger(__name__)


def get_latency(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info("Time elapsed for %s: %.3f ms", func.__qualname__, elapsed_ms)

    return wrapper
