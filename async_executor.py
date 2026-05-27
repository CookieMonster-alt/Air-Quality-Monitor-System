import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, Coroutine

class AILOAsyncExecutor:
    """
    Asynchronous bridge managing background heavy workloads.
    Constrained to max_workers=2 to prevent Raspberry Pi CPU throttling.
    """
    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def run_in_background(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Executes a blocking synchronous function in the thread pool without
        freezing the asyncio event loop.
        """
        loop = asyncio.get_running_loop()
        # run_in_executor requires positional arguments
        # If kwargs are passed, we wrap the function call in a lambda
        if kwargs:
            wrapped_func = lambda: func(*args, **kwargs)
            return await loop.run_in_executor(self.executor, wrapped_func)
        else:
            return await loop.run_in_executor(self.executor, func, *args)

    def shutdown(self):
        """Clean teardown of the thread pool."""
        self.executor.shutdown(wait=True)

# Export a singleton instance for global dependency injection
ailo_executor = AILOAsyncExecutor()
