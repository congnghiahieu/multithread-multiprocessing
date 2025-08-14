import asyncio
import os


def show_info():
    print(f"Running in thread pool worker. PID={os.getpid()}")


async def main():
    loop = asyncio.get_running_loop()
    # Trigger creation of the default executor
    await loop.run_in_executor(None, show_info)
    default_exec = (
        loop._default_executor
    )  # Undocumented attribute, but works for inspection
    print(f"Default executor type: {type(default_exec)}")
    print(f"Default max_workers: {default_exec._max_workers}")


asyncio.run(main())
