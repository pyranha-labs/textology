"""Utilities for running tasks in parallel."""

from __future__ import annotations

import multiprocessing
import threading
from concurrent import futures
from multiprocessing.context import BaseContext
from types import TracebackType
from typing import Any
from typing import Callable
from typing import Generator
from typing import Iterable


class ParallelPoolExecutor:
    """A pool of threads or processes to run asynchronous tasks in parallel.

    Closely matches `concurrent.futures.Executor` interfaces for greatest parity. Additional logic added
    to control indexing, ordering, multiprocess context handling, and cleanup.

    This pool is safe to use with Textual while an application is showing. Compared to `multiprocessing.pool.ThreadPool`
    and `multiprocessing.pool.Pool`, this should not encounter errors with file descriptors.

    Example:
        import urllib.request

        URLS = [
            'https://docs.python.org/3.9/library/',
            'https://docs.python.org/3.10/library/',
            'https://docs.python.org/3.11/library/',
            'https://docs.python.org/3.12/library/',
        ]

        def load_url(url: str, timeout: int) -> bytes:
            with urllib.request.urlopen(url, timeout=timeout) as conn:
                return conn.read()

        with ParallelPoolExecutor(max_workers=3) as pool:
            pool.submit(
                funcs=[load_url for url in URLS],
                func_args=[(url, 60) for url in URLS],
            )
            for result in pool.as_completed():
                print(len(result))
    """

    def __init__(
        self,
        max_workers: int | None = None,
        use_threads: bool = True,
        thread_name_prefix: str = "",
        mp_context: BaseContext | str | None = None,
        initializer: Callable[[], None] | None = None,
        initargs: tuple = (),
        clear_results: bool = True,
    ) -> None:
        """Create an executor pool of threads or processes that can execute calls in parallel.

        Args:
            max_workers: The maximum amount of threads/processes that can be used to execute the calls.
                See `concurrent.futures.ThreadPoolExecutor` and `concurrent.futures.ProcessPoolExecutor` for defaults.
            use_threads: Use multithreading instead of multiprocessing to improve resource management.
                Threads are recommended for I/O bound tasks, or CPU bound tasks which release the GIL.
            thread_name_prefix: An optional name prefix to give threads.
            mp_context: A multiprocessing context, or name, to launch the workers if threading is disabled.
                e.g. 'fork', 'forkserver', and 'spawn'.
            initializer: A callable used to initialize worker threads/processes.
            initargs: A tuple of arguments to pass to the initializer.
            clear_results: Whether to dereference future results after yield to allow faster garbage collection.
        """
        self._clear_results = clear_results
        self._completed = 0
        self._submitted = 0
        self._futures: dict[int, futures.Future] = {}
        self._ready: dict[int, Any] = {}

        if use_threads:
            self._executor = futures.ThreadPoolExecutor(  # pylint: disable=consider-using-with
                max_workers=max_workers,
                thread_name_prefix=thread_name_prefix,
                initializer=initializer,
                initargs=initargs,
            )
        else:
            mp_context = multiprocessing.get_context(mp_context) if isinstance(mp_context, str) else mp_context
            self._executor = futures.ProcessPoolExecutor(  # pylint: disable=consider-using-with
                max_workers=max_workers,
                mp_context=mp_context,
                initializer=initializer,
                initargs=initargs,
            )

    def __enter__(self) -> ParallelPoolExecutor:
        """Create an executor pool that will automatically release resources on exit."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> bool:
        """Release the executor pool resources."""
        self.shutdown()
        return False

    def as_completed(
        self,
        ordered: bool = False,
        with_index: bool = False,
        exit_on_error: bool = True,
    ) -> Generator[Any | tuple[int, Any], None, None]:
        """Iterate over results as each pending Future completes.

        Args:
            ordered: Return completed results in the same order requested.
                Pending results remain in memory until yielded.
            with_index: Return the index of the result with the result.
            exit_on_error: Whether to raise and abort on exceptions, or pass the exceptions as results.

        Yields:
            Result of a completed future if indexing is disabled, or index and result if enabled.
        """
        if self._completed == self._submitted:
            self._executor.shutdown()
            return
        if len(self._workers) == 0:
            raise futures.BrokenExecutor("All workers in pool terminated prematurely")

        for future in futures.as_completed(self._futures.values()):
            future_index, future_result = future.result()
            self._ready[future_index] = future_result
            self._futures.pop(future_index)
            if self._clear_results:
                # Dereference the future result value after it was yielded to allow garbage collection ASAP.
                future._result = None  # pylint: disable=protected-access
            for index, result in sorted(self._ready.items()) if ordered else list(self._ready.items()):
                if ordered and index != self._completed:
                    continue
                self._ready.pop(index)
                self._completed += 1
                if isinstance(result, BaseException) and exit_on_error:
                    raise result
                if with_index:
                    yield (index, result) if with_index else result
                else:
                    yield result

    @staticmethod  # Use static method to prevent pickling issues with subprocessing pools.
    def _call_with_index(
        index: int,
        func: Callable,
        args: Iterable,
        kwargs: dict[str, Any],
    ) -> tuple[int, Any]:
        """Run a function, capture failures, and return the index representing the future."""
        try:
            result = func(*args, **kwargs)
        except BaseException as error:  # pylint: disable=broad-except
            result = error
        return index, result

    @property
    def completed(self) -> int:
        """Number of tasks completed by the pool over its lifetime."""
        return self._completed

    def shutdown(self, wait: bool = False, *, cancel_futures: bool = True) -> None:
        """Stop the executor pool and release resources.

        This method is safe to call several times. No other methods can be called after this one.
        Processes will exit immediately. Threads will run until their active tasks complete.
        If interrupting threads is needed, the functions submitted must provide their own interruptions.

        Args:
            wait: Wait until all running futures have finished, and the resources used by the executor are reclaimed.
            cancel_futures: Cancel all pending futures. Futures that are completed or running will not be cancelled.
        """
        # Snapshot active workers before shutdown to ensure cleanup can be performed.
        # Shutdown will clear the active workers, even if they are still running.
        workers = self._workers
        try:
            self._executor.shutdown(wait=wait, cancel_futures=cancel_futures)
        finally:
            self._futures.clear()
            self._ready.clear()
            if isinstance(self._executor, futures.ProcessPoolExecutor):
                self._stop_processes(workers)

    @staticmethod
    def _stop_processes(workers: dict[int, multiprocessing.Process]) -> None:
        """Stop any running processes used by the executor pool.

        Do not call directly. Should only be called by executor pool on shutdown.

        Mimics `multiprocessing.Pool` to attempt graceful, immediate, shutdowns.
        Sends termination signals, waits (joins), and finally kills, if processes fail to exit successfully.
        Additional cleanup will be attempted by python before exit if any fail to stop.
        """
        try:
            for process in workers.values():
                if process.exitcode is None:
                    process.terminate()
        finally:
            try:
                for process in workers.values():
                    if process.is_alive():
                        process.join()
            finally:
                for process in workers.values():
                    if process.is_alive():
                        process.kill()

    def submit(
        self,
        funcs: Callable | list[Callable],
        func_args: tuple | list[tuple] | None = None,
        func_kwargs: dict | list[dict] | None = None,
    ) -> list[futures.Future]:
        """Submit callables to be executed with the given arguments.

        Schedules the callables to be executed as func(*args, **kwargs), and returns Future instances representing
        the execution of the callables.

        Args:
            funcs: One or more callables to be submitted to the pool to be run by the executor workers.
                Execution will begin immediately if any workers are idle.
            func_args: Positional arguments to send to the functions.
                Number of argument sets must match number of functions. Use None if no positional arguments are used.
            func_kwargs: Keyword arguments to send to the functions.
                Number of argument sets must match number of functions. Use None if no keyword arguments are used.

        Returns:
            One Future for each call.
        """
        if not isinstance(funcs, list):
            funcs = [funcs]
        if func_args is not None and not isinstance(func_args, list):
            func_args = [func_args]
        if func_kwargs is not None and not isinstance(func_kwargs, list):
            func_kwargs = [func_kwargs]

        # Ensure there is an arg and kwarg set for every function. Arguments are optional, but the amount provided must
        # match function length in order to be zipped, otherwise functions could be skipped.
        if not func_args:
            func_args = [() for _ in funcs]
        if len(funcs) != len(func_args):
            raise ValueError(
                f"Length of positional argument sets does not match number of functions: {len(func_args)}/{len(funcs)}"
            )
        if not func_kwargs:
            func_kwargs = [{} for _ in funcs]
        if len(funcs) != len(func_kwargs):
            raise ValueError(
                f"Length of keyword argument sets does not match number of functions: {len(func_kwargs)}/{len(funcs)}"
            )

        new_futures = []
        for index, (func, args, kwargs) in enumerate(zip(funcs, func_args, func_kwargs)):
            index += self._submitted
            future = self._executor.submit(self._call_with_index, index, func, args, kwargs)
            new_futures.append(future)
            self._futures[index] = future
        self._submitted += len(funcs)
        return new_futures

    @property
    def submitted(self) -> int:
        """Number of tasks submitted to the pool over its lifetime."""
        return self._submitted

    @property
    def _workers(self) -> dict[int, multiprocessing.Process] | set[threading.Thread]:
        """The active executor pool workers."""
        if isinstance(self._executor, futures.ThreadPoolExecutor):
            workers = self._executor._threads or set()  # pylint: disable=protected-access
        else:
            workers = self._executor._processes or {}  # pylint: disable=protected-access
        return workers


def parallelize(
    funcs: list[Callable],
    func_args: list[tuple] | None = None,
    func_kwargs: list[dict] | None = None,
    max_workers: int = None,
    use_threads: bool = True,
    mp_context: BaseContext | str | None = "fork",
    with_index: bool = False,
    ordered: bool = False,
    exit_on_error: bool = True,
) -> Generator[Any | tuple[int, Any] | Any, None, None]:
    """Run functions using a parallel processing pool.

    Args:
        funcs: Functions to run in parallel.
        func_args: Positional arguments to send to the functions.
            Number of argument sets must match number of functions. Use None if no positional arguments are used.
        func_kwargs: Keyword arguments to send to the functions.
            Number of argument sets must match number of functions. Use None if no keyword arguments are used.
        max_workers: Maximum number of workers to use to execute the functions.
        use_threads: Use multithreading instead of multiprocessing to improve resource management.
            Threads are recommended for I/O bound tasks, or CPU bound tasks which release the GIL.
        mp_context: A multiprocessing context, or name, to launch the workers if threading is disabled.
            e.g. 'fork', 'forkserver', and 'spawn'.
        ordered: Return completed results in the same order requested. Other results wait in memory until yielded.
        with_index: Return the index of the result with the result. Allows for tracking without forcing ordered.
        exit_on_error: Whether to raise and abort on exceptions, or pass the exceptions as results.

    Yields:
        Result of a completed future if indexing is disabled, or index and result if enabled.
    """
    with ParallelPoolExecutor(
        max_workers=max_workers,
        use_threads=use_threads,
        mp_context=mp_context,
    ) as pool:
        pool.submit(funcs, func_args=func_args, func_kwargs=func_kwargs)
        for result in pool.as_completed(ordered=ordered, with_index=with_index, exit_on_error=exit_on_error):
            yield result
