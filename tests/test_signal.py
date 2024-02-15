# path: tests/test_signal.py

import asyncio
import pytest
from f2.utils._signal import SignalManager


def run_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_task())


@pytest.mark.asyncio
async def test_task():
    print("Start long running task...")
    for _ in range(10):
        if SignalManager.is_shutdown_signaled():
            print("Stopping task early due to shutdown signal.")
            break
        print("Still working...")
        await asyncio.sleep(0.1)
    print("End of long running task.")


if __name__ == "__main__":
    run_task()
