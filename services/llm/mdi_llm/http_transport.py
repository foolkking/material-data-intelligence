"""Bound the complete provider exchange, including partial headers and bodies."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import math
import urllib.error
import urllib.request
from typing import Callable

import httpx


class InvalidProviderResponse(ValueError):
    pass


class ProviderStreamCancelled(Exception):
    """The owning request no longer accepts model output."""


def read_provider_response(
    request: urllib.request.Request, *, timeout: float, byte_limit: int,
    on_chunk: Callable[[bytes], None] | None = None,
) -> bytes:
    """Read at most limit + 1 bytes so callers retain their size-error contract.

    A socket inactivity timeout alone is insufficient: a provider can keep a
    worker alive indefinitely by sending a byte before each read timeout.
    Canceling the async exchange also closes its connection before returning.
    """
    if not math.isfinite(timeout) or timeout <= 0 or byte_limit < 1:
        raise ValueError("Invalid provider HTTP limits")

    async def exchange() -> bytes:
        headers = dict(request.header_items())
        headers["Accept-Encoding"] = "identity"
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            async with client.stream(request.get_method(), request.full_url, headers=headers, content=request.data) as response:
                if response.status_code >= 300:
                    # Keep retry timing, but never attach an upstream URL,
                    # credential, response body or free-form reason to errors.
                    retry_headers = {"Retry-After": response.headers["Retry-After"]} if "Retry-After" in response.headers else {}
                    raise urllib.error.HTTPError("", response.status_code, "Provider HTTP request failed", retry_headers, None)
                body = bytearray()
                async for chunk in response.aiter_raw():
                    body.extend(chunk[:byte_limit + 1 - len(body)])
                    if len(body) > byte_limit:
                        break
                    if on_chunk is not None:
                        on_chunk(chunk)
                return bytes(body)

    async def bounded() -> bytes:
        try:
            async with asyncio.timeout(timeout):
                return await exchange()
        except (TimeoutError, httpx.TimeoutException):
            raise TimeoutError("Provider request deadline exceeded") from None
        except httpx.RemoteProtocolError:
            raise InvalidProviderResponse("Provider response was incomplete or invalid") from None
        except httpx.HTTPError:
            raise urllib.error.URLError("Provider connection failed") from None

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(bounded())
    # Preserve the synchronous adapter contract for callers already running
    # an event loop. This private executor is joined after the bounded call.
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="mdi-provider-http") as executor:
        return executor.submit(lambda: asyncio.run(bounded())).result()
