import asyncio
import threading
from typing import Optional

from backend.core.base_service import TraceableService

class LoopManager (TraceableService):
    """
    LoopManager: start/stop a background asyncio event loop in a daemon thread.
    Use run_coro_sync(coro, timeout) to schedule coroutines on that loop and wait.
    """
    def __init__(self):
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._ready = threading.Event()

    def _start_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        # signal ready before running forever
        self._ready.set()
        try:
            self._loop.run_forever()
        finally:
            # best-effort cleanup
            pending = asyncio.all_tasks(loop=self._loop)
            for t in pending:
                t.cancel()
            try:
                self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            finally:
                self._loop.close()

    def start(self, wait_ready: bool = True, timeout: int = 5):
        """Start background loop thread. Idempotent."""
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._start_loop, daemon=True)
        self._thread.start()
        if wait_ready and not self._ready.wait(timeout=timeout):
            raise RuntimeError("Async loop failed to start")

    def stop(self, join_timeout: int = 5):
        """Stop background loop and join thread."""
        if not self._loop:
            return
        # stop loop thread-safe
        try:
            self._loop.call_soon_threadsafe(self._loop.stop)
        except Exception:
            pass
        if self._thread:
            self._thread.join(timeout=join_timeout)

    def is_ready(self) -> bool:
        return self._ready.is_set()

    def run_coro_sync(self, coro, timeout: int = None):
        """
        Schedule coroutine on the background loop and wait for result.
        Raises exceptions from the coroutine.
        """
        if not self._loop:
            raise RuntimeError("Event loop not started")
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return fut.result(timeout)
    

loop_mgr = LoopManager()
loop_mgr.start()  