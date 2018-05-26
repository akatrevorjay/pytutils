import asyncio


def async_limit_concurrent(max_in_flight=1):
    @wrapt.decorator
    def _inner(wrapped, instance, args, kwargs):
        limiter = asyncio.Semaphore(value=max_in_flight)

        is_not_limited = asyncio.Event()
        is_not_limited.set()

        async def _backoff(self, timeout=10):
            if not is_not_limited.is_set():
                await is_not_limited.wait()
            else:
                log.debug(
                    'Hit API limit; waiting %d seconds until trying again.', timeout,
                )

                is_not_limited.clear()
                await asyncio.sleep(timeout)
                is_not_limited.set()

        async with limiter.acquire():
            await is_not_limited.wait()

            res = wrapped(*args, **kwargs)
            return res

    return _inner

